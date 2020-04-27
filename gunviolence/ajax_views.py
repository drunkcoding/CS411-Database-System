from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
from .utils import *
from .models import *
from .forms import *
import asyncio

@require_http_methods(["POST"])
def saveIncidentID(request):
    incident_id = int(request.POST.get('incident_id'))

    settings.LOGGER.info('saveIncidentID', request.POST)

    if incident_id > 0 and incident_id != None:
        request.session['incident_id'] = incident_id
        return JsonResponse({'Retcode':0})

    return JsonResponse({'Retcode':-1})

async def __deleteIncident(id):
    if id == None or len(id) == 0: return
    incident_id = int(id)
    GunViolence.objects.filter(id=incident_id).delete()

@require_http_methods(["POST"])
def deleteIncident(request):
    settings.LOGGER.info('delete', request.POST)
    id = request.POST.get('id')
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    asyncio.ensure_future(__deleteIncident(id))
    return JsonResponse({'Retcode':0})

@require_http_methods(["POST"])
def saveMapMeta(request):
    request.session['map_zoom'] = float(request.POST.get('map_zoom'))
    request.session['map_center'] = [float(x) for x in request.POST.getlist('map_center[]')]

    return JsonResponse({'Retcode':0})

@require_http_methods(["POST"])
def saveIncident(request):
    # print('saveIncident', request.POST)

    incident_form = IncidentForm({
        'id': int(request.POST.get('id')) if request.POST.get('id') else None,
        'date': datetime.datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date(),
        'state': request.POST.get('state'),
        'address': request.POST.get('address'),
        'n_killed': int(request.POST.get('n_killed')),
        'n_injured': int(request.POST.get('n_injured')),
        'latitude': float(request.POST.get('latitude')),
        'longitude': float(request.POST.get('longitude')),
        # 'notes': request.POST.get('notes'),
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

    obj = GunViolence()

    obj.date = incident_form['date'].value()
    obj.state = State.objects.get(pk=incident_form['state'].value())
    obj.address = incident_form['address'].value()
    obj.n_killed = incident_form['n_killed'].value()
    obj.n_injured = incident_form['n_injured'].value()
    obj.latitude = incident_form['latitude'].value()
    obj.longitude = incident_form['longitude'].value()
    # obj.notes = incident_form['notes'].value()

    obj.characteristics = formset2JSON(characteristic_formset)
    obj.guns = formset2JSON(gun_formset)
    obj.participants = formset2JSON(participant_formset)

    with transaction.atomic():
        if incident_form['id'].value() != None: 
            GunViolence.objects.filter(id=incident_form['id'].value()).delete()
        obj.save()

        for form in gun_formset:
            gun = form.cleaned_data
            gun_obj, created = Gun.objects.get_or_create(
                incident=obj,
                type = gun.get('gun_type'),
                stolen = gun.get('stolen'),
            )
        for form in participant_formset:
            participant = form.cleaned_data
            part_obj, created = Participant.objects.get_or_create(
                incident = obj,
                name = participant.get('name'),
                age = participant.get('age'),
                gender = participant.get('gender'),
                status = participant.get('status'),
                type = participant.get('type'),
                relationship = participant.get('relationship'),
            )

    return JsonResponse({'Retcode':0})

@require_http_methods(["GET"])
def getFullTextSearch(request):
    text = request.GET.get('text')
    if text is None: return JsonResponse([])

    date_form = DateRangeForm(request.session.get('date_form'))
    if not date_form.is_valid(): return JsonResponse([])

    date_form = date_form.cleaned_data

    from_date = date_form['from_date'].strftime("%Y-%m-%d")
    to_date = date_form['to_date'].strftime("%Y-%m-%d")

    result = GunViolence.objects.raw(
        f"\
        SELECT id,date,latitude,longitude,address,n_killed,n_injured,city,state_id\
        FROM `antientropy_cs411`.`gunviolence_gunviolence` \
        WHERE MATCH(`city`, `address`, `participants`, `characteristics`, `guns`, `state_id`) \
        AGAINST('{text}') \
        AND date BETWEEN '{from_date}' AND '{to_date}' \
        ORDER BY RAND() \
        LIMIT 10;\
        "
        )
    
    data = []
    for p in result:
        data.append({
            "date":p.date.strftime("%Y-%m-%d"), 
            "latitude":p.latitude, 
            "longitude":p.longitude, 
            "address":p.address,
            "n_killed":p.n_killed,
            "n_injured":p.n_injured,
            "city":p.city,
            "state":p.state.name,
        })
    return JsonResponse(data, safe=False)
