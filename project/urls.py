"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path

from gunviolence.views import *
from gunviolence.data_views import *
from gunviolence.ajax_views import *

urlpatterns = [
    path('', dashboard),
    path('save_map_meta/', saveMapMeta, name='save_map_meta'),
    path('save_incident_form/', saveIncidentForm, name='save_incident_form'),
    path('save_characteristic_formset/', saveCharacteristicFormSet, name='save_characteristic_formset'),
    path('save_gun_formset/', saveGunFormSet, name='save_gun_formset'),
    path('save_participant_formset/', saveParticipantFormSet, name='save_participant_formset'),
    # path('select_location/', selectLocation, name='select_location'),
    path('delete_incident/', deleteIncident, name='delete_incident'),
    path('save_incident_id/', saveIncidentID, name='save_incident_id'),
    path('save_incident/', saveIncident, name='save_incident'),
    path('manual_input/', manualInputRaw, name= 'manual_input'),
    # path('state_count/<state>/', stateCountEachDate, name='state_count'),
]
