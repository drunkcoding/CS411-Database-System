from django import forms
from django.conf import settings
from .models import *
import datetime

class SQLForm(forms.Form):
    query = forms.CharField(label='rawsql', max_length=1024)

class DateRangeForm(forms.Form):
    from_date = forms.DateField(initial=datetime.date(year=2014,month=4,day=11))
    to_date = forms.DateField(initial=datetime.date(year=2014,month=4,day=12))

class IncidentForm(forms.Form):
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    state = forms.CharField()
    address = forms.CharField(required=False, max_length=1024)
    n_killed = forms.IntegerField(min_value=0)
    n_injured = forms.IntegerField(min_value=0)
    latitude = forms.FloatField(min_value=-90, max_value=90)
    longitude = forms.FloatField(min_value=-180, max_value=180)

class CharacteristicForm(forms.Form):
    characteristic = forms.CharField()

CharacteristicFormSet = forms.formset_factory(CharacteristicForm, can_delete=True, extra=1)

class GunForm(forms.Form):
    stolen = forms.CharField()
    gun_type = forms.CharField(max_length=64)

GunFormSet = forms.formset_factory(GunForm, can_delete=True, extra=1)
class ParticipantForm(forms.Form):
    name = forms.CharField(max_length=256)
    status = forms.CharField()
    age = forms.IntegerField(min_value=0)
    age_group = forms.CharField(max_length=256)
    type = forms.CharField()
    gender = forms.CharField()
    relationship = forms.CharField()

ParticipantFormSet = forms.formset_factory(ParticipantForm, can_delete=True, extra=1)
