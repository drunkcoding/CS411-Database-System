from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(State)
admin.site.register(City)
admin.site.register(Location)
admin.site.register(IncidentCharacteristic)
admin.site.register(UserProfile)
admin.site.register(GunViolence)
admin.site.register(Participant)