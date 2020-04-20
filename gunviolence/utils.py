from django.db.models import Sum, F
from django.conf import settings
import re, os
import json
import pandas as pd

from .models import *

def formsetEncode(formset, field):
    data = [(i,form.cleaned_data[field]) for i, form in enumerate(formset) if 'DELETE' in form.cleaned_data and not form.cleaned_data['DELETE']]
    return '||'.join(["%s:%s" % tup for tup in data])

def formsetDecode(formset, field):
    return formset(initial=json.loads(field))

def Json2formset(form, data):
    data = json.loads(data)
    formset = []
    for ele in data:
        formset.append(form(ele))
    return formset     

def formset2Json(formset):
    data = [form.cleaned_data for form in formset if form.is_valid()]
    return json.dumps(data)
"""
def formsetEncode(formset, field):
    data = [form.cleaned_data for i, form in enumerate(formset) if 'DELETE' in form.cleaned_data and not form.cleaned_data['DELETE']]
    return json.dumps(data)

def formsetDecode(formset, field):
    return formset(initial=json.loads(field))
"""

def filterGunViolenceEmptyData():
    return GunViolenceJson.objects\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\

def requestTotalCount(date_form):
    if date_form is None or not date_form.is_valid(): return None
    return filterGunViolenceEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .aggregate(total_killed=Sum('n_killed'), total_injured=Sum('n_injured'))

def requestStateCount(date_form):
    state_count = list(
        filterGunViolenceEmptyData()\
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


def requestCaseLocation(date_form):
    locations = list(
        filterGunViolenceEmptyData()\
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
