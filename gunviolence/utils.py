from .models import *
from django.db.models import Sum, F
import re
import json

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

def filterGunViolenceRawEmptyData():
    return GunViolenceJson.objects\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\

def requestTotalCount(date_form):
    if date_form is None or not date_form.is_valid(): return None
    return filterGunViolenceRawEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .aggregate(total_killed=Sum('n_killed'), total_injured=Sum('n_injured'))

def requestStateCount(date_form):
    if date_form is None or not date_form.is_valid(): return None
    return list(
        filterGunViolenceRawEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('state').annotate(total_harm=Sum(F('n_killed')+F('n_injured'))).order_by('-total_harm')
    )

def requestCaseLocation(date_form):
    if date_form is None or not date_form.is_valid(): return None
    locations = list(
        filterGunViolenceRawEmptyData()\
        .filter(date__range=[date_form.cleaned_data['from_date'], date_form.cleaned_data['to_date']])\
        .values('id', 'latitude', 'longitude', "n_killed", "n_injured").order_by('?')
        )
    return locations[:min(len(locations), 5000)]
