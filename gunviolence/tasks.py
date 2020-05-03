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

def getField(field):
    return None if pd.isna(field) else field

def splitCell(cell):
    return re.split("\|\|", cell)

def extractCharacteristics(row):
    if pd.isna(row['incident_characteristics']): return []
    s = splitCell(row['incident_characteristics'])
    return [{'characteristic': x} for x in s]

def extractGuns(row):
    if pd.isna(row['gun_stolen']) or pd.isna(row['gun_type']): return []
    stolen = splitCell(row['gun_stolen'])
    type = splitCell(row['gun_type'])
    return [{'type':type[i], 'stolen':stolen[i]} for i in range(len(stolen))]

def extractFields(field, data, fname):
    if pd.isna(field): return
    split = splitCell(field.lower())
    for s in split:
        ss = re.split("::", s)
        if len(ss) != 2: continue
        if not ss[0] in data: data[ss[0]] = {}
        data[ss[0]][fname] = ss[1]

def extractParticipants(row):
    if pd.isna(row['participant_type']) \
    and pd.isna(row['participant_status']) \
    and pd.isna(row['participant_relationship']) \
    and pd.isna(row['participant_name']) \
    and pd.isna(row['participant_gender']) \
    and pd.isna(row['participant_age_group']) \
    and pd.isna(row['participant_age']) : return []

    data = {}

    extractFields(row['participant_type'], data, "type")
    extractFields(row['participant_status'], data, "status")
    extractFields(row['participant_relationship'], data, "relationship")
    extractFields(row['participant_name'], data, "name")
    extractFields(row['participant_type'], data, "type")
    extractFields(row['participant_gender'], data, "gender")
    extractFields(row['participant_age_group'], data, "age_group")
    extractFields(row['participant_age'], data, "age")

    return [v for k, v in data.items()]


def processRow(row):
    data = {}
    data['details'] = {}
    data['id'] = row['incident_id']
    data['source'] = row['source_url']
    data['date'] = datetime.strptime(row['date'], '%m/%d/%Y').strftime('%m-%d-%Y')
    data['state'] = row['state']
    data['city'] = row['city_or_county']
    data['address'] = row['address']
    data['lat'] = row['latitude']
    data['lng'] = row['longitude']
    data['killed'] = row['n_killed']
    data['injured'] = row['n_injured']

    data['details']['url'] = row['incident_url']
    data['details']['congressional_district'] = getField(row['congressional_district'])
    data['details']['state_senate_district'] = getField(row['state_senate_district'])
    data['details']['state_house_district'] = getField(row['state_house_district'])
    data['details']['characteristics'] = extractCharacteristics(row)
    data['details']['participants'] = extractParticipants(row)
    data['details']['guns'] = extractGuns(row)

    insertData(data)

@background(schedule=0)
def importOriginalData():
    fpath = os.path.join(settings.MEDIA_DIR, "gun-violence-data_cleaned.csv")
    df = pd.read_csv(os.path.abspath(fpath), engine='python')

    print(df.head())

    pool = Pool(10)
    pool.map(insertData, [row for index, row in df.iterrows()])

    #for index, row in df.iterrows():
    #    processRow(row)

@background(schedule=0)
def crawlNewIncidents():
    fpath = os.path.join(os.path.join(settings.BASE_DIR, "gunviolence"), "crawler")
    try:
        os.system(f"python {os.path.abspath(os.path.join(fpath, 'update_data.py'))}")
        os.system(f"python {os.path.abspath(os.path.join(fpath, 'update_incidents.py'))}")
        full_data_path = os.path.join(fpath, "mass_shootings.json")
        with open(full_data_path, 'r') as fp:
            full_data = json.load(fp)
        for item in full_data:
            insertData(item)
    except:
        return

#importOriginalData()
#crawlNewIncidents(repeat=Task.DAILY)
