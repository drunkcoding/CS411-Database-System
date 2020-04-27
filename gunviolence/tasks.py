import re
import os
from .models import *
from multiprocessing import Pool, freeze_support, cpu_count
import pandas as pd
import torch
import time
import json
from datetime import datetime
from background_task.models import Task
from background_task import background
from django.conf import settings
import django
django.setup()


def insertData(item):
    state = State.objects.get(pk=item.get('state'))

    incident, created = GunViolence.objects.get_or_create(
        id=item.get('id'),
        date=datetime.strptime(item.get('date'), settings.DATE_FORMAT).date(),
        state=state,
        city=item.get('city'),
        latitude=item.get('lat'),
        longitude=item.get('lng'),
        address=item.get('address'),
        n_killed=item.get('killed'),
        n_injured=item.get('injured'),
        congressional_district=item.get('congressional_district'),
        state_house_district=item.get('state_house_district'),
        state_senate_district=item.get('state_senate_district'),
        participants=json.dumps(
            item.get('details', {}).get('participants', [])),
        characteristics=json.dumps(
            item.get('details', {}).get('characteristics', [])),
        guns=json.dumps(item.get('details', {}).get('guns', [])),
    )

    participants = item.get('details', {}).get('participants', [])
    characteristics = item.get('details', {}).get('characteristics', [])
    guns = item.get('details', {}).get('guns', [])

    for gun in guns:
        obj, created = Gun.objects.get_or_create(
            incident=incident,
            type=gun.get('type'),
            stolen=gun.get('stolen'),
        )

    """
    for characteristic in characteristics:
        obj, created = Characteristic.objects.get_or_create(
            incident_id=incident,
            characteristic = characteristic.get('characteristic'),
        ) 
    """
    for participant in participants:
        obj, created = Participant.objects.get_or_create(
            incident=incident,
            name=participant.get('name'),
            age=participant.get('age'),
            gender=participant.get('gender'),
            status=participant.get('status'),
            type=participant.get('type'),
            relationship=participant.get('relationship'),
        )


@background(schedule=0)
def importOriginalData():
    full_data_path = os.path.join(settings.MEDIA_DIR, "data.json")
    with open(full_data_path, 'r') as fp:
        full_data = json.load(fp)
    pool = Pool(10)
    pool.map(insertData, [item for item in full_data])

@background(schedule=0)
def crawlNewIncidents():
    fpath = os.path.join(os.path.join(settings.BASE_DIR, "gunviolence"), "crawler")
    try:
        os.system(f"python {os.path.abspath(os.path.join(fpath, 'update_data.py'))}")
        os.system(f"python {os.path.abspath(os.path.join(fpath, 'update_incidents.py'))}")
        full_data_path = os.path.join(settings.MEDIA_DIR, "mass_shootings.json")
        with open(full_data_path, 'r') as fp:
            full_data = json.load(fp)
        for item in full_data:
            insertData(item)
    except:
        return

#importOriginalData()
#crawlNewIncidents(repeat=Task.DAILY)
