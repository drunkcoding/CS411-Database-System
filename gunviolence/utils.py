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

def JSON2Formset(form, data):
    data = json.loads(data)
    formset = []
    for ele in data:
        formset.append(form(ele))
    return formset     

def formset2JSON(formset):
    data = [form.cleaned_data for form in formset if form.is_valid()]
    return json.dumps(data)
"""
def formsetEncode(formset, field):
    data = [form.cleaned_data for i, form in enumerate(formset) if 'DELETE' in form.cleaned_data and not form.cleaned_data['DELETE']]
    return json.dumps(data)

def formsetDecode(formset, field):
    return formset(initial=json.loads(field))
"""

def filterGVEmptyData():
    return GunViolence.objects\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .exclude(latitude=0.0, longitude=0.0)\
