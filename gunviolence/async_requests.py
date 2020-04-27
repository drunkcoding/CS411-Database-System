import asyncio
import pandas as pd
from django.db.models import Sum, F, Q
from django.conf import settings
import re, os, json
from .models import *
from .utils import *
from .forms import *
from collections import Counter
import datetime


common_words = [
            "the", "be", "a", "an", "and", "of", "to", "in", "am", "is", "are",
            "at", "not", "that", "have", "i", "it", "for", "on", "with", "he",
            "she", "as", "you", "do", "this", "but", "his", "by", "from",
            "they", "we", "her", "or", "will", "my", "one", "all", "s", "if",
            "any", "our", "may", "your", "these", "d", " ", "me", "so", "what",
            "him", "their", "no", "other", "during", "open", "lost", "found", "non",
            "use", "without", "found"
        ]

async def requestKilledEachState(date_form):
    total_killed = list(filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_killed=Sum(F('n_killed'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_killed'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_killed.csv")
    df = df.pivot_table(values='n_killed', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def requestInjuredEachState(date_form):
    total_killed = list(filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_injured=Sum(F('n_injured'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_injured'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_injured.csv")
    df = df.pivot_table(values='n_injured', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def requestHarmedEachState(date_form):
    total_killed = list(filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('date', 'state').annotate(n_harmed=Sum(F('n_injured') + F('n_killed'))))
    df = pd.DataFrame(total_killed, columns=['date','state', 'n_harmed'])
    fpath = os.path.join(settings.MEDIA_DIR, "n_harmed.csv")
    df = df.pivot_table(values='n_harmed', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath)

async def requestCharactristicWords(date_form):
    rows = list(filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .exclude(characteristics="[]")\
        .filter(characteristics__isnull=False)\
        .values('characteristics', 'state').all())
    
    data = []
    for row in rows:
        ch = json.loads(row['characteristics'])
        state = row['state']
        words = []
        for c in ch:
            s = re.split("[^a-zA-Z-]", c['characteristic'].lower())
            for w in s: 
                w = w.strip()
                if len(w) > 0 and not w in common_words and w != '-':
                    words.append(w)
        counter = Counter(words)
        for word, count in dict(counter).items():
            data.append({'state':state, 'word':word, 'size':count})
    fpath = os.path.join(settings.MEDIA_DIR, "characteristics.csv")
    df = pd.DataFrame(data)
    #df = df.pivot_table(values='size', index='date', columns = 'state', aggfunc='sum', fill_value=0.0)
    df.to_csv(fpath, index = False)

async def requestParticipantAge(date_form):
    rows = list(Participant.objects\
        .filter(incident__date__range=(date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']))\
        .filter(age__isnull=False)\
        .values('incident__state', 'age')
        .all()
        )
    fpath = os.path.join(settings.MEDIA_DIR, "participant_age.csv")
    df = pd.DataFrame(rows)
    df.to_csv(fpath, index = False)

async def requestRecentUpdate():
    rows = list(filterGVEmptyData()\
        .values('id', 'update_time', 'latitude', 'longitude', 'city').order_by('-update_time').all()[:20]
        )
    fpath = os.path.join(settings.MEDIA_DIR, "recent_update.csv")

    df = pd.DataFrame(rows)
    df.to_csv(fpath, index = False)

async def requestDataForms(id, ctx):
    if id == None: return
    try:
        incident = GunViolence.objects.get(id=id)
    except:
        return
    if incident is None: return
    ctx['incident_form'] = IncidentForm(initial={
        'id':incident.id,
        'date':incident.date,
        'state':incident.state.name,
        'address':incident.address,
        'n_killed':incident.n_killed,
        'n_injured':incident.n_injured,
        'latitude':incident.latitude,
        'longitude':incident.longitude,
    })
    ctx['gun_formset'] = JSON2Formset(GunForm, incident.guns)
    ctx['characteristic_formset'] = JSON2Formset(CharacteristicForm, incident.characteristics)
    ctx['participant_formset'] = JSON2Formset(ParticipantForm, incident.participants)
    ctx['scroll'] = True

async def requestTotalCount(date_form):
    return filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .aggregate(total_killed=Sum('n_killed'), total_injured=Sum('n_injured'))

async def requestStateCount(date_form):
    state_count = list(
        filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('state').annotate(total_harm=Sum(F('n_killed')+F('n_injured'))).order_by('-total_harm')
    )
    df_state_count = pd.DataFrame(state_count)

    fpath = os.path.join(settings.MEDIA_DIR, "gz_states.json")
    with open(fpath, 'r') as fp:
        states = json.load(fp)
        for i in range(len(states['features'])):
            states['features'][i]['properties']['involve'] = 0
            for row in state_count:
                if row['state'] == states['features'][i]['properties']['NAME']:
                    n_involve = int(row['total_harm'])
                    states['features'][i]['properties']['involve'] = n_involve
                    break
    with open(fpath, 'w') as fp:
        json.dump(states, fp)

    return df_state_count.total_harm.min(), df_state_count.total_harm.max(), state_count

async def requestCaseLocation(date_form):
    locations = list(
        filterGVEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('id', 'latitude', 'longitude', "n_killed", "n_injured").order_by('?')
        )
    locations = locations[:min(len(locations), 5000)]

    df_location = pd.DataFrame(locations)
    df_location['total_harm'] = df_location.n_killed + df_location.n_injured

    points = {
            "type": "FeatureCollection",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": []
        }

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
    fpath = os.path.join(settings.MEDIA_DIR, "points.json")
    with open(fpath, 'w') as fp:
        json.dump(points, fp)

    return df_location.total_harm.min(), df_location.total_harm.max()
