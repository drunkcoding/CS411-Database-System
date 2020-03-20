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
    date = forms.DateField()
    state = forms.ChoiceField(choices=settings.STATE_CHOICES)
    address = forms.CharField(required=False, max_length=1024)
    n_killed = forms.IntegerField(min_value=0)
    n_injured = forms.IntegerField(min_value=0)
    latitude = forms.FloatField(min_value=-90, max_value=90)
    longitude = forms.FloatField(min_value=-180, max_value=180)
    location_description = forms.CharField(required=False, max_length=1024)
    notes = forms.CharField(required=False, max_length=1024)

class CharacteristicForm(forms.Form):
    characteristic = forms.ChoiceField(choices=settings.CHARACTER_CHOICES)

CharacteristicFormSet = forms.formset_factory(CharacteristicForm, can_delete=True)

class GunForm(forms.Form):
    stolen = forms.ChoiceField(choices=settings.GUNSTOLEN_CHOICES)
    type = forms.CharField(max_length=64)

GunFormSet = forms.formset_factory(GunForm, can_delete=True)
class ParticipantForm(forms.Form):
    name = forms.CharField(max_length=256)
    status = forms.ChoiceField(choices=settings.HARM_CHOICES)
    age = forms.IntegerField(min_value=0)
    type = forms.ChoiceField(choices=settings.PTYPE_CHOICES)
    gender = forms.ChoiceField(choices=settings.GENDER_CHOICES)
    relationship = forms.ChoiceField(choices=settings.RELATION_CHOICES)

ParticipantFormSet = forms.formset_factory(ParticipantForm, can_delete=True)    