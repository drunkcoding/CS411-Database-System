import json, re
import pandas as pd
from datetime import datetime

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
        

df = pd.read_csv("gun-violence-data_cleaned.csv", engine='python')

print(df.head())

output_data = []
for index, row in df.iterrows():
    #print(row)
    #print(row['gun_stolen'])

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
    
    output_data.append(data)

with open('data.json', 'w') as fp:
    json.dump(output_data, fp)
