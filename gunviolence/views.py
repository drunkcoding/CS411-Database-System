import csv, io, os, logging, json, sys
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection
from django.db.models import Sum, F
from django.http import JsonResponse
from .models import *
from .forms import *

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

    date_range = DateRangeForm()

    if request.method == 'POST':
        date_range = DateRangeForm(request.POST)

    if date_range.is_valid():
        request.session['date_range'] = request.POST

        total_count = GunViolenceRaw.objects\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .filter(source_url__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\
        .filter(date__range=[date_range.cleaned_data['from_date'], date_range.cleaned_data['to_date']])\
        .aggregate(total_killed=Sum('n_killed'), total_injured=Sum('n_injured'))

        return render(
            request, 
            'dashboard.html', 
            {
                'daterange':date_range,
                'total_killed': total_count['total_killed'],
                'total_injured': total_count['total_injured'],
            }
        )

    return render(
        request, 
        'dashboard.html', 
        {
            'daterange':date_range,
        }
    )


def heatmap(request):

    points = {
            "type": "FeatureCollection",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": []
        }

    states = settings.GEOSTATES.copy()    

    date_range = DateRangeForm(request.session.get('date_range'))

    state_min = 0
    state_max = 1

    case_min = 0
    case_max = 1

    if date_range.is_valid():
        locations = GunViolenceRaw.objects.all()\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .filter(source_url__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\
        .filter(date__range=[date_range.cleaned_data['from_date'], date_range.cleaned_data['to_date']])\
        .values('latitude', 'longitude', "n_killed", "n_injured", "source_url")

        state_sum = GunViolenceRaw.objects.all()\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .filter(source_url__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\
        .filter(date__range=[date_range.cleaned_data['from_date'], date_range.cleaned_data['to_date']])\
        .values('state').annotate(n_killed=Sum('n_killed'), n_injured=Sum('n_injured'))

        case_max = 0
        case_min = 1000

        for location in locations:
            n_involve = location['n_killed']+location['n_injured']
            points['features'].append(
                { 
                    "type": "Feature", 
                    "properties": {
                        "involve": n_involve,
                        "source_url": location['source_url']
                    }, 
                    "geometry": { "type": "Point", "coordinates": [ location['longitude'], location['latitude'], 0.0 ] }
                } 
            )
            if n_involve < case_min: case_min = n_involve
            if n_involve > case_max: case_max = n_involve
        
        state_min = 1000000000
        state_max = 0
        for i in range(len(states['features'])):
            states['features'][i]['properties']['involve'] = 0
            for row in state_sum:
                if row['state'] == states['features'][i]['properties']['NAME']:
                    n_involve = int(row['n_killed']) + int(row['n_injured'])
                    states['features'][i]['properties']['involve'] = n_involve / states['features'][i]['properties']['CENSUSAREA'] * 100000
                    if n_involve < state_min: state_min = n_involve
                    if n_involve > state_max: state_max = n_involve
                    break
    
    return render(
        request, 
        'heatmap.html', 
        {
            'points':json.dumps(points), 
            'daterange':date_range, 
            'states':json.dumps(states),
            'state_min':state_min,
            'state_max':state_max,
            'case_min':case_min,
            'case_max':case_max,
            'mapbox_token': settings.MAPBOX_TOKEN,
        }
    )

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