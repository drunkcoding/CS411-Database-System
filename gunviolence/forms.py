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
    state = forms.CharField()
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

class ManualInputForm(forms.ModelForm):
    class Meta:
        model = GunViolenceRaw
        fields = ['date', 'state', 'city_or_county']


        #
        # fields = ['incident_id', 'date', 'state', 'city_or_county', 'address',
        # 'n_killed', 'n_injured', 'source_url', 'incident_url_fields_missing',
        # 'congressional_district', 'gun_stolen', 'gun_type', 'incident_characteristics',
        # 'latitude', 'location_description', 'longitude', 'n_guns_involved',
        # 'notes', 'participant_age', 'participant_age_group', 'participant_gender',
        # 'participant_name', 'participant_relationship', 'participant_status',
        # 'participant_type', 'sources', 'state_house_district', 'state_senate_district']
