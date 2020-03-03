import csv, io, os, logging, json, sys
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection

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
"""
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