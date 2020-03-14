import csv, io, os, logging, json, sys
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection
from django.db.models import Sum, F
from django.http import JsonResponse
from .models import *
from .forms import *
from .utils import *

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

    if total_count != None: total_count = requestTotalCount(date_form)

    if state_count != None: 
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

    map_zoom = request.session.get('map_zoom')
    map_center = request.session.get('map_center')

    if map_zoom: context['map_zoom'] = map_zoom;
    if map_center: context['map_center'] = map_center;

    return render(request, template_name, context)

def saveMapMeta(request):

    request.session['map_zoom'] = float(request.GET.get('map_zoom'))
    request.session['map_center'] = [float(x) for x in request.GET.getlist('map_center[]')]

    return JsonResponse({})

def testpage(request):
    template_name = 'test.html'
    context = {}

    return render(request, template_name, context)

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