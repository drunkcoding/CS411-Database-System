from django import forms

class SQLForm(forms.Form):
    query = forms.CharField(label='rawsql', max_length=1024)