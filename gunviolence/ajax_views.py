from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
from .utils import *
from .models import *
from .forms import *

@require_http_methods(["POST"])
def saveIncidentID(request):
    incident_id = int(request.POST.get('incident_id'))

    settings.LOGGER.info('saveIncidentID', request.POST)

    if incident_id > 0 and incident_id != None:
        request.session['incident_id'] = incident_id
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

@require_http_methods(["POST"])
def deleteIncident(request):
    settings.LOGGER.info('delete', request.POST)

    id = request.POST.get('id')
    if id == None or len(id) == 0: return JsonResponse({'Retcode':0})
    incident_id = int(id)

    GunViolenceJson.objects.filter(id=incident_id).delete()

    try:
        del request.session['incident_id']
    except:
        pass

    return JsonResponse({'Retcode':0})

@require_http_methods(["POST"])
def saveMapMeta(request):
    request.session['map_zoom'] = float(request.POST.get('map_zoom'))
    request.session['map_center'] = [float(x) for x in request.POST.getlist('map_center[]')]

    return JsonResponse({'Retcode':0})

@require_http_methods(["POST"])
def saveIncidentForm(request):
    incident_form = IncidentForm(request.POST)
    if incident_form.is_valid():
        request.session['incident_form'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

@require_http_methods(["POST"])
def saveCharacteristicFormSet(request):
    characteristic_formset = CharacteristicFormSet(request.POST)
    if characteristic_formset.is_valid():
        request.session['characteristic_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

@require_http_methods(["POST"])
def saveGunFormSet(request):
    gun_formset = GunFormSet(request.POST)
    if gun_formset.is_valid():
        request.session['gun_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

@require_http_methods(["POST"])
def saveParticipantFormSet(request):
    participant_formset = ParticipantFormSet(request.POST)
    if participant_formset.is_valid():
        request.session['participant_formset'] = request.POST
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

@require_http_methods(["POST"])
def saveIncident(request):
    settings.LOGGER.info('saveIncident', request.POST)

    incident_form = IncidentForm({
        'id': int(request.POST.get('id')) if request.POST.get('id') else None,
        'date': datetime.datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date(),
        'state': request.POST.get('state'),
        'address': request.POST.get('address'),
        'n_killed': int(request.POST.get('n_killed')),
        'n_injured': int(request.POST.get('n_injured')),
        'latitude': float(request.POST.get('latitude')),
        'longitude': float(request.POST.get('longitude')),
        'notes': request.POST.get('notes'),
    })

    gun_formset = []
    participant_formset = []
    characteristic_formset = []
    if request.POST.get('gun_type'):
        gun_formset = [GunForm({
            'stolen': request.POST.getlist('stolen')[i],
            'gun_type': request.POST.getlist('gun_type')[i],
        }) for i in range(len(request.POST.getlist('gun_type')))]

    if request.POST.get('characteristic'):
        characteristic_formset = [CharacteristicForm({
            'characteristic': request.POST.getlist('characteristic')[i],
        }) for i in range(len(request.POST.getlist('characteristic')))]   

    if request.POST.get('type'):
        participant_formset = [ParticipantForm({
            'name': request.POST.getlist('name')[i],
            'status': request.POST.getlist('status')[i],
            'age': int(request.POST.getlist('age')[i]),
            'age_group': request.POST.getlist('age_group')[i],
            'type': request.POST.getlist('type')[i],
            'gender': request.POST.getlist('gender')[i],
            'relationship': request.POST.getlist('relationship')[i],
        }) for i in range(len(request.POST.getlist('type')))]  

    try:
        del request.session['incident_id']
    except:
        pass


    obj = GunViolenceJson()

    obj.date = incident_form['date'].value()
    obj.state = incident_form['state'].value()
    obj.address = incident_form['address'].value()
    obj.n_killed = incident_form['n_killed'].value()
    obj.n_injured = incident_form['n_injured'].value()
    obj.latitude = incident_form['latitude'].value()
    obj.longitude = incident_form['longitude'].value()
    obj.notes = incident_form['notes'].value()

    obj.characteristics = formset2Json(characteristic_formset)
    obj.guns = formset2Json(gun_formset)
    obj.participants = formset2Json(participant_formset)

    with transaction.atomic():
        if incident_form['id'].value() != None: 
            GunViolenceJson.objects.filter(id=incident_form['id'].value()).delete()
        obj.save()

    return JsonResponse({'Retcode':0})
