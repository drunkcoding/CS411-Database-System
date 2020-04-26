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

from django.urls import path
from django.conf.urls.static import static

from gunviolence.views import *
from gunviolence.ajax_views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('save_map_meta/', saveMapMeta, name='save_map_meta'),
    path('delete_incident/', deleteIncident, name='delete_incident'),
    path('save_incident_id/', saveIncidentID, name='save_incident_id'),
    path('save_incident/', saveIncident, name='save_incident'),
    path('get_fulltext/', getFullTextSearch, name='get_fulltext'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
