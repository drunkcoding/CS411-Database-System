from .models import *
from django.db.models import Sum, F

def formsetFormat(formset, field):
    data = [(i,form.cleaned_data[field]) for i, form in enumerate(formset) if 'DELETE' in form.cleaned_data and not form.cleaned_data['DELETE']]
    return '||'.join(["%s:%s" % tup for tup in data])

def filterGunViolenceRawEmptyData():
    return GunViolenceRaw.objects\
        .filter(latitude__isnull=False, longitude__isnull=False)\
        .filter(n_killed__isnull=False, n_injured__isnull=False)\
        .filter(source_url__isnull=False)\
        .filter(incident_url__isnull=False)\
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
        .values('incident_id', 'latitude', 'longitude', "n_killed", "n_injured", "incident_url").order_by('?')
        )
    return locations[:min(len(locations), 5000)]