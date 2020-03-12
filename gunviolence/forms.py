from django import forms
from .models import *
import datetime

class SQLForm(forms.Form):
    query = forms.CharField(label='rawsql', max_length=1024)

class DateRangeForm(forms.Form):
    from_date = forms.DateField(initial=datetime.date(year=2014,month=4,day=11))
    to_date = forms.DateField(initial=datetime.date(year=2014,month=4,day=12))

class IncidentForm(forms.ModelForm):
    class Meta:
        model = GunViolenceRaw
        fields = '__all__'    
