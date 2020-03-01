import csv, io, os, logging
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.db import transaction

from .models import *

"""
def homepage(request):
    template = "index.html"
    context = {}
    return render(request, template, context)

# Create your views here.
def dummy(request):

    template = "dummy.html"
    context = {}

    if request.method != 'POST':
        return render(request, template, context)

    state_file = os.path.join(settings.MEDIA_DIR, "state.csv")
    city_file = os.path.join(settings.MEDIA_DIR, "city.csv")
    data_file = os.path.join(settings.MEDIA_DIR, "gun-violence-data.csv")

    state_df = pd.read_csv(state_file, header=0)
    city_df = pd.read_csv(city_file, header=0)
    data_df = pd.read_csv(data_file, header=0)

    Location.objects.all().delete()
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

    locations = {}

    data_df = data_df.dropna(subset=['latitude', 'longitude'])

    with transaction.atomic():
        for index, row in data_df.iterrows():
            if row['city_or_county'] in cities:
                location, created = Location.objects.get_or_create(
                    latitude=row['latitude'],
                    state = states[row['state']],
                    longitude = row['longitude'],
                    city = cities[row['city_or_county']]
                )
                locations[row['incident_id']] = location
            else:
                logging.info("%s, %s skipped" % (row['city_or_county'], row['state']))

    logging.info("locations import completed")

    return render(request, template, context)    
"""