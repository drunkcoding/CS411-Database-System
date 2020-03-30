import csv, io, os, logging, json, sys, datetime
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection
from django.http import JsonResponse, HttpResponse
from .models import *
from .forms import *
from .utils import *

import logging
logger = logging.getLogger(__name__)

def dashboard(request):
    """
    with open(os.path.join(settings.MEDIA_DIR, 'mass_shootings_full.json'), 'rb') as f:
        data = json.load(f)
        
        for item in data:
            incident, created = GunViolenceJson.objects.get_or_create(
                id=item.get('id'),
                date=datetime.datetime.strptime(item.get('date'), '%Y-%m-%d').date(),
                state = item.get('state'),
                city = item.get('city'),
                latitude = item.get('lat'),
                longitude = item.get('lng'),
                address = item.get('address'),
                n_killed = item.get('killed'),
                n_injured = item.get('injured'),
                participants = json.dumps(item.get('details', {}).get('participants', [])),
                characteristics = json.dumps([{'characteristic': x} for x in item.get('details', {}).get('characteristics', [])]),
                guns = json.dumps(item.get('details', {}).get('guns', [])),
            )
    """
    template_name = 'dashboard.html'
    context = {}
    context['date_form'] = DateRangeForm()
    context['states'] = settings.GEOSTATES.copy()
    context['characteristic_form'] = CharacteristicForm()
    context['participant_form'] = ParticipantForm()
    context['gun_form'] = GunForm()
    #context['characteristic_formset'] = CharacteristicFormSet()
    #context['gun_formset'] = GunFormSet()
    context['incident_form'] = IncidentForm()
    #context['participant_formset'] = ParticipantFormSet()

    print(request.POST)
    
    incident_id = request.session.get('incident_id')
    if incident_id != None:
        print("incident_id", incident_id)
        incident = GunViolenceJson.objects.get(id=incident_id)
        if incident:
            context['incident_form'] = IncidentForm(initial={
                'id':incident.id,
                'date':incident.date,
                'state':incident.state,
                'address':incident.address,
                'n_killed':incident.n_killed,
                'n_injured':incident.n_injured,
                'latitude':incident.latitude,
                'longitude':incident.longitude,
                'notes':incident.notes,
            })
            print(json.loads(incident.characteristics))
            print(json.loads(incident.guns))
            print(json.loads(incident.participants))
            context['gun_formset'] = Json2formset(GunForm, incident.guns)
            context['characteristic_formset'] = Json2formset(CharacteristicForm, incident.characteristics)
            context['participant_formset'] = Json2formset(ParticipantForm, incident.participants)

        del request.session['incident_id']
        context['scroll_to_form'] = True

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
                    "incident_id": location['id'],
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

    context['points'] = json.dumps(points)
    context['date_form'] = date_form
    context['states'] = json.dumps(states)
    context['state_min'] = state_min
    context['state_max'] = state_max
    context['case_min'] = case_min
    context['case_max'] = case_max

    context['date_form'] = date_form
    context['total_count'] = total_count
    context['state_count'] = state_count

    request.session['total_count'] = total_count
    request.session['date_form'] = request.POST
    request.session['state_count'] = state_count

    context['map_zoom'] = request.session.get('map_zoom')
    context['map_center'] = request.session.get('map_center')

    return render(request, template_name, context)

"""
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
        obj.incident_url_fields_missing = "FALSE"

        obj.incident_characteristics = formsetEncode(characteristic_formset, 'characteristic')
        obj.gun_stolen = formsetEncode(gun_formset, 'stolen')
        obj.gun_type = formsetEncode(gun_formset, 'type')
        obj.participant_name = formsetEncode(participant_formset, 'name')
        obj.participant_status = formsetEncode(participant_formset, 'status')
        obj.participant_age = formsetEncode(participant_formset, 'age')
        obj.participant_type = formsetEncode(participant_formset, 'type')
        obj.participant_gender = formsetEncode(participant_formset, 'gender')
        obj.participant_relationship = formsetEncode(participant_formset, 'relationship')

        obj.save()

    return render(request, template_name, context)
"""

def manualInputRaw(request):
    if request.method == 'POST':
        filled_form = ManualInputForm(request.POST)
        if filled_form.is_valid():
            filled_form.save()
            note = 'Data input successful!'
            new_form = ManualInputForm()
            return render(request, 'manualInput.html', {'manualInputForm':new_form, 'note':note})
    else:
        form = ManualInputForm()
        return render(request, 'manualInput.html', {'manualInputForm':form})

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
