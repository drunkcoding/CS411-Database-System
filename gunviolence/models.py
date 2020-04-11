import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class State(models.Model):
    name = models.CharField(max_length=64)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()

    class Meta:
        managed = False
        db_table = 'gunviolence_state'

class City(models.Model):
    name = models.CharField(max_length=64)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()
    state = models.ForeignKey('State', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gunviolence_city'

class GunViolence(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=200)
    date = models.DateField()
    city = models.ForeignKey(City, models.DO_NOTHING)
    latitude = models.FloatField()
    longitude = models.FloatField()
    state = models.ForeignKey('State', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolence'

class IncidentCharacteristic(models.Model):
    gunviolence = models.ForeignKey(GunViolence, models.DO_NOTHING)
    incidentcharacteristic = models.ForeignKey('Incidentcharacteristic', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolence_characteristic'
        unique_together = (('gunviolence', 'incidentcharacteristic'),)

class IncidentCharacteristic(models.Model):
    characteristic = models.CharField(max_length=1024)
    count = models.PositiveIntegerField()
    city = models.ForeignKey(City, models.DO_NOTHING)
    state = models.ForeignKey('State', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_incidentcharacteristic'

class Participant(models.Model):
    name = models.CharField(max_length=64)
    age = models.PositiveSmallIntegerField()
    gender = models.PositiveSmallIntegerField()
    harm = models.PositiveSmallIntegerField()
    type = models.PositiveSmallIntegerField()
    relationship = models.PositiveSmallIntegerField(blank=True, null=True)
    involve = models.ForeignKey(GunViolence, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_participant'

class GunViolenceJson(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    state = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    latitude =  models.FloatField(null=True)
    longitude =  models.FloatField(null=True)
    address = models.TextField(null=True)
    n_killed = models.PositiveSmallIntegerField(null=True)
    n_injured = models.PositiveSmallIntegerField(null=True)
    participants = models.TextField(null=True)
    characteristics = models.TextField(null=True)
    guns = models.TextField(null=True)
    notes = models.TextField(null=True)

class GunViolenceRaw(models.Model):
    incident_id = models.AutoField(primary_key=True)
    date = models.DateField()
    state = models.CharField(max_length=64)
    city_or_county = models.CharField(max_length=64)
    address = models.TextField(null=True)
    n_killed = models.PositiveSmallIntegerField(null=True)
    n_injured = models.PositiveSmallIntegerField(null=True)
    incident_url = models.URLField(null=True)
    source_url = models.URLField(null=True)
    incident_url_fields_missing = models.CharField(max_length=8, null=True)
    congressional_district = models.PositiveSmallIntegerField(null=True)
    gun_stolen = models.CharField(max_length=64, null=True)
    gun_type = models.CharField(max_length=64, null=True)
    incident_characteristics = models.TextField(null=True)
    latitude =  models.FloatField(null=True)
    location_description = models.TextField(null=True)
    longitude =  models.FloatField(null=True)
    n_guns_involved = models.PositiveSmallIntegerField(null=True)
    notes = models.TextField(null=True)
    participant_age = models.TextField(null=True)
    participant_age_group = models.TextField(null=True)
    participant_gender = models.TextField(null=True)
    participant_name = models.TextField(null=True)
    participant_relationship = models.TextField(null=True)
    participant_status = models.TextField(null=True)
    participant_type = models.TextField(null=True)
    sources = models.URLField(null=True)
    state_house_district = models.PositiveSmallIntegerField(null=True)
    state_senate_district = models.PositiveSmallIntegerField(null=True)
