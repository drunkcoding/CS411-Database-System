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
    context['characteristic_form'] = CharacteristicForm()
    context['participant_form'] = ParticipantForm()
    context['gun_form'] = GunForm()
    context['incident_form'] = IncidentForm()
    context['scroll'] = False

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    tasks = []
    rtasks = []

    settings.LOGGER.info('dashboard', request.POST)
    
    incident_id = request.GET.get('incident_id', None)
    tasks.append(requestDataForms(incident_id, context))

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

    if request.method == 'POST' and request.POST.get('from_date', None) != None:
        date_form = DateRangeForm(request.POST)

    if not date_form.is_valid():
        # print("partial context", context)
        loop.run_until_complete(asyncio.gather(*tasks))
        return render(request, template_name, context)

    tasks.append(loop.create_task(requestHarmedEachState(date_form)))
    tasks.append(loop.create_task(requestCharactristicWords(date_form)))
    tasks.append(loop.create_task(requestParticipantAge(date_form)))

    rtasks.append(loop.create_task(requestTotalCount(date_form)))
    rtasks.append(loop.create_task(requestStateCount(date_form)))
    rtasks.append(loop.create_task(requestCaseLocation(date_form)))

    """
    from_date = date_form.from_date.strftime("%Y-%m-%d")
    to_date = date_form.to_date.strftime("%Y-%m-%d")

    cursor = connection.cursor()
    cursor.execute(
        f"CREATE OR REPLACE VIEW gv_view AS \
        SELECT * FROM gunviolence_gunviolence \
        WHERE date BETWEEN {from_date} AND {to_date};"
    )
    """

    total_count, state, case = loop.run_until_complete(asyncio.gather(*rtasks))

    state_min, state_max, state_count = state
    case_min, case_max = case

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

    # print("full context", context)

    loop.run_until_complete(asyncio.gather(*tasks))
    return render(request, template_name, context)
