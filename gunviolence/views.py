import csv, io, os, logging, json, sys
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection
from django.db.models import Sum, F
from django.http import JsonResponse, HttpResponse
from .models import *
from .forms import *
from .utils import *

import uuid
import logging
logger = logging.getLogger(__name__)

"""
def homepage(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SQLForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            query = form.cleaned_data['query']

            cursor = connection.cursor()
            try:            
                cursor.execute(query)
            except:
                return render(request, 'sample-query.html', {'form': SQLForm(), 'sqldata': json.dumps([[str(sys.exc_info()[1])]])})
            data = cursor.fetchall()
            return render(request, 'sample-query.html', {'form': SQLForm(), 'sqldata': json.dumps(data)})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SQLForm()

    return render(request, 'sample-query.html', {'form': form})
"""

def dashboard(request):

    template_name = 'dashboard.html'
    context = {}
    context['date_form'] = DateRangeForm()

    date_form = DateRangeForm(request.session.get('date_form'))
    total_count = request.session.get('total_count')
    state_count = request.session.get('state_count')
    display_chart = request.session.get('display_chart')
    locations = []

    state_min = 0
    state_max = 1

    case_min = 0
    case_max = 1

    if request.method == 'POST':
        date_form = DateRangeForm(request.POST)

    if not date_form.is_valid(): return render(request, template_name, context)

    total_count = requestTotalCount(date_form)
    
    state_count = requestStateCount(date_form)
    df_state_count = pd.DataFrame(state_count)
    state_min = df_state_count.total_harm.min()
    state_max = df_state_count.total_harm.max()

    locations = requestCaseLocation(date_form)
    df_location = pd.DataFrame(locations)
    df_location['total_harm'] = df_location.n_killed + df_location.n_injured
    case_min = df_location.total_harm.min()
    case_max = df_location.total_harm.max()

    points = {
            "type": "FeatureCollection",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": []
        }

    states = settings.GEOSTATES.copy()    

    for location in locations:
        n_involve = location['n_killed'] + location['n_injured']
        points['features'].append(
            { 
                "type": "Feature", 
                "properties": {
                    "involve": n_involve,
                    "incident_id": location['incident_id'],
                    "source_url": location['incident_url'],
                }, 
                "geometry": { "type": "Point", "coordinates": [ location['longitude'], location['latitude'], 0.0 ] }
            }
        )

    if state_count != None:    
        for i in range(len(states['features'])):
            states['features'][i]['properties']['involve'] = 0
            for row in state_count:
                if row['state'] == states['features'][i]['properties']['NAME']:
                    n_involve = int(row['total_harm'])
                    states['features'][i]['properties']['involve'] = n_involve
                    break

    context = {
            'points':json.dumps(points), 
            'date_form':date_form, 
            'states':json.dumps(states),
            'state_min':state_min,
            'state_max':state_max,
            'case_min':case_min,
            'case_max':case_max,
        }


    context['date_form'] = date_form
    context['total_count'] = total_count
    context['state_count'] = state_count

    request.session['total_count'] = total_count
    request.session['date_form'] = request.POST
    request.session['state_count'] = state_count

    context['map_zoom'] = request.session.get('map_zoom')
    context['map_center'] = request.session.get('map_center')

    return render(request, template_name, context)

def deleteIncident(request):
    if request.method == 'POST':
        incident_id = int(request.POST.get('incident_id'))
        GunViolenceRaw.objects.filter(incident_id=incident_id).delete()

    return JsonResponse({})

def saveMapMeta(request):
    request.session['map_zoom'] = float(request.POST.get('map_zoom'))
    request.session['map_center'] = [float(x) for x in request.POST.getlist('map_center[]')]

    return JsonResponse({})

def saveIncidentForm(request):
    incident_form = IncidentForm(request.POST)
    print(request.POST)
    if incident_form.is_valid(): 
        request.session['incident_form'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})    

def saveCharacteristicFormSet(request):
    characteristic_formset = CharacteristicFormSet(request.POST)
    if characteristic_formset.is_valid(): 
        request.session['characteristic_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})    

def saveGunFormSet(request):
    gun_formset = GunFormSet(request.POST)
    if gun_formset.is_valid(): 
        request.session['gun_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})  

def saveParticipantFormSet(request):
    participant_formset = ParticipantFormSet(request.POST)
    if participant_formset.is_valid(): 
        request.session['participant_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})      

def selectLocation(request):
    template_name = 'select_location.html'
    context = {}
    context['characteristic_formset'] = CharacteristicFormSet()
    context['gun_formset'] = GunFormSet()
    context['incident_form'] = IncidentForm()
    context['participant_formset'] = ParticipantFormSet()
    context['states'] = settings.GEOSTATES.copy()

    if request.method == 'GET': return render(request, template_name, context)

    participant_formset = ParticipantFormSet(request.session.get('participant_formset'))
    characteristic_formset = CharacteristicFormSet(request.session.get('characteristic_formset'))
    gun_formset = GunFormSet(request.session.get('gun_formset'))
    incident_form = IncidentForm(request.session.get('incident_form'))

    try:
        del request.session['characteristic_formset']
        del request.session['gun_formset']
        del request.session['incident_form']
        del request.session['participant_formset']
    except:
        pass

    if participant_formset.is_valid() and characteristic_formset.is_valid() and gun_formset.is_valid() and incident_form.is_valid():
        obj = GunViolenceRaw()

        obj.date = incident_form['date'].value()
        obj.state = incident_form['state'].value()
        obj.address = incident_form['address'].value()
        obj.n_killed = incident_form['n_killed'].value()
        obj.n_injured = incident_form['n_injured'].value()
        obj.latitude = incident_form['latitude'].value()
        obj.longitude = incident_form['longitude'].value()
        obj.notes = incident_form['notes'].value()
        obj.location_description = incident_form['location_description'].value()
        obj.incident_url_fields_missing = "FALSE"

        obj.incident_characteristics = formsetFormat(characteristic_formset, 'characteristic')
        obj.gun_stolen = formsetFormat(gun_formset, 'stolen')
        obj.gun_type = formsetFormat(gun_formset, 'type')
        obj.participant_name = formsetFormat(participant_formset, 'name')
        obj.participant_status = formsetFormat(participant_formset, 'status')
        obj.participant_age = formsetFormat(participant_formset, 'age')
        obj.participant_type = formsetFormat(participant_formset, 'type')
        obj.participant_gender = formsetFormat(participant_formset, 'gender')
        obj.participant_relationship = formsetFormat(participant_formset, 'relationship')

        obj.save()

    return render(request, template_name, context)
"""
def testpage(request):
    template_name = 'test.html'
    context = {}

    return render(request, template_name, context)
"""

"""
# Create your views here.
def dummy(request):

    template = "dummy.html"
    context = {}

    if request.method != 'POST':
        return render(request, template, context)

    state_file = os.path.join(settings.MEDIA_DIR, "state.csv")
    city_file = os.path.join(settings.MEDIA_DIR, "city.csv")
    character_file = os.path.join(settings.MEDIA_DIR, "character.csv")
    #data_file = os.path.join(settings.MEDIA_DIR, "gun-violence-data.csv")

    state_df = pd.read_csv(state_file, header=0)
    city_df = pd.read_csv(city_file, header=0)
    character_df = pd.read_csv(character_file, header=0)
    #data_df = pd.read_csv(data_file, header=0)

    # Location.objects.all().delete()
    # City.objects.all().delete()
    # State.objects.all().delete()

    states = {}

    with transaction.atomic():
        for index, row in state_df.iterrows():
            state, created = State.objects.get_or_create(
                name=row['name'], 
                population=row['population'], 
                land_area = row['land_area']
            )
            states[row['name']] = state

    cities = {}

    with transaction.atomic():
        for index, row in city_df.iterrows():
            city, created = City.objects.get_or_create(
                name=row['name'],
                state = states[row['state']],
                population = row['population'],
                land_area = row['land_area']
            )
            cities[row['name']] = city

    return render(request, template, context)    
"""