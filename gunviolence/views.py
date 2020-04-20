import csv, io, os, logging, json, sys, datetime
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction, connection
from django.http import JsonResponse, HttpResponse
from .models import *
from .forms import *
from .utils import *
from .async_requests import *

def dashboard(request):
    template_name = 'dashboard.html'
    context = {}
    context['date_form'] = DateRangeForm()
    context['characteristic_form'] = CharacteristicForm()
    context['participant_form'] = ParticipantForm()
    context['gun_form'] = GunForm()
    #context['characteristic_formset'] = CharacteristicFormSet()
    #context['gun_formset'] = GunFormSet()
    context['incident_form'] = IncidentForm()
    #context['participant_formset'] = ParticipantFormSet()

    settings.LOGGER.info('dashboard', request.POST)
    
    incident_id = request.session.get('incident_id')
    if incident_id != None:
        print("incident_id", incident_id)
        incident = GunViolenceJson.objects.get(id=incident_id)
        if incident:
            context['incident_form'] = IncidentForm(initial={
                'id':incident.id,
                'date':incident.date,
                'state':incident.state,
                'address':incident.address,
                'n_killed':incident.n_killed,
                'n_injured':incident.n_injured,
                'latitude':incident.latitude,
                'longitude':incident.longitude,
            })
            context['gun_formset'] = Json2formset(GunForm, incident.guns)
            context['characteristic_formset'] = Json2formset(CharacteristicForm, incident.characteristics)
            context['participant_formset'] = Json2formset(ParticipantForm, incident.participants)

        del request.session['incident_id']
        context['scroll_to_form'] = True

    date_form = DateRangeForm(request.session.get('date_form'))
    total_count = request.session.get('total_count')
    state_count = request.session.get('state_count')
    state_min, state_max = request.session.get('state_range', default=(0,1))
    case_min, case_max = request.session.get('case_range', default=(0,1))
    
    context['date_form'] = date_form
    context['total_count'] = total_count
    context['state_count'] = state_count
    context['state_min'] = state_min
    context['state_max'] = state_max
    context['case_min'] = case_min
    context['case_max'] = case_max

    if request.method == 'POST':
        date_form = DateRangeForm(request.POST)

    if not date_form.is_valid(): return render(request, template_name, context)

    asyncio.run(scheduleAsyncRequests(date_form))

    total_count = requestTotalCount(date_form)

    state_min, state_max, state_count = requestStateCount(date_form)
    case_min, case_max = requestCaseLocation(date_form)

    context['date_form'] = date_form
    context['state_min'] = state_min
    context['state_max'] = state_max
    context['case_min'] = case_min
    context['case_max'] = case_max

    context['total_count'] = total_count
    context['state_count'] = state_count

    request.session['total_count'] = total_count
    request.session['date_form'] = request.POST
    request.session['state_count'] = state_count
    request.session['state_range'] = (state_min, state_max)
    request.session['case_range'] = (case_min, case_max)

    context['map_zoom'] = request.session.get('map_zoom')
    context['map_center'] = request.session.get('map_center')

    return render(request, template_name, context)
