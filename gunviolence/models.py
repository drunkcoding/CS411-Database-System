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
    state = models.ForeignKey('GunviolenceState', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gunviolence_city'

class Gunviolence(models.Model):
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=200)
    date = models.DateField()
    city = models.ForeignKey(GunviolenceCity, models.DO_NOTHING)
    latitude = models.FloatField()
    longitude = models.FloatField()
    state = models.ForeignKey('GunviolenceState', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolence'

class GunviolenceCharacteristic(models.Model):
    gunviolence = models.ForeignKey(GunviolenceGunviolence, models.DO_NOTHING)
    incidentcharacteristic = models.ForeignKey('GunviolenceIncidentcharacteristic', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolence_characteristic'
        unique_together = (('gunviolence', 'incidentcharacteristic'),)

class Gunviolenceraw(models.Model):
    incident_id = models.AutoField(primary_key=True)
    date = models.DateField()
    state = models.CharField(max_length=64)
    city_or_county = models.CharField(max_length=64)
    address = models.TextField(blank=True, null=True)
    n_killed = models.PositiveSmallIntegerField(blank=True, null=True)
    n_injured = models.PositiveSmallIntegerField(blank=True, null=True)
    incident_url = models.CharField(max_length=200, blank=True, null=True)
    source_url = models.CharField(max_length=200, blank=True, null=True)
    incident_url_fields_missing = models.CharField(max_length=8)
    congressional_district = models.PositiveSmallIntegerField(blank=True, null=True)
    gun_stolen = models.CharField(max_length=64, blank=True, null=True)
    gun_type = models.CharField(max_length=64, blank=True, null=True)
    incident_characteristics = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    location_description = models.TextField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    n_guns_involved = models.PositiveSmallIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    participant_age = models.TextField(blank=True, null=True)
    participant_age_group = models.TextField(blank=True, null=True)
    participant_gender = models.TextField(blank=True, null=True)
    participant_name = models.TextField(blank=True, null=True)
    participant_relationship = models.TextField(blank=True, null=True)
    participant_status = models.TextField(blank=True, null=True)
    participant_type = models.TextField(blank=True, null=True)
    sources = models.CharField(max_length=200, blank=True, null=True)
    state_house_district = models.PositiveSmallIntegerField(blank=True, null=True)
    state_senate_district = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolenceraw'


class Incidentcharacteristic(models.Model):
    characteristic = models.CharField(max_length=1024)
    count = models.PositiveIntegerField()
    city = models.ForeignKey(GunviolenceCity, models.DO_NOTHING)
    state = models.ForeignKey('GunviolenceState', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_incidentcharacteristic'


class GunviolenceOrigin(models.Model):
    incident_id = models.IntegerField(blank=True, null=True)
    date = models.DateField(db_column='DATE', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(max_length=64, blank=True, null=True)
    city_or_county = models.CharField(max_length=128, blank=True, null=True)
    address = models.CharField(max_length=1024, blank=True, null=True)
    n_killed = models.IntegerField(blank=True, null=True)
    n_injured = models.IntegerField(blank=True, null=True)
    incident_url = models.CharField(max_length=1024, blank=True, null=True)
    source_url = models.CharField(max_length=1024, blank=True, null=True)
    incident_url_fields_missing = models.CharField(max_length=10, blank=True, null=True)
    congressional_district = models.IntegerField(blank=True, null=True)
    gun_stolen = models.CharField(max_length=1024, blank=True, null=True)
    gun_type = models.CharField(max_length=1024, blank=True, null=True)
    incident_characteristics = models.CharField(max_length=1024, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    location_description = models.CharField(max_length=1024, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    n_guns_involved = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=1024, blank=True, null=True)
    participant_age = models.CharField(max_length=1024, blank=True, null=True)
    participant_age_group = models.CharField(max_length=1024, blank=True, null=True)
    participant_gender = models.CharField(max_length=1024, blank=True, null=True)
    participant_name = models.CharField(max_length=1024, blank=True, null=True)
    participant_relationship = models.CharField(max_length=1024, blank=True, null=True)
    participant_status = models.CharField(max_length=1024, blank=True, null=True)
    participant_type = models.CharField(max_length=1024, blank=True, null=True)
    sources = models.CharField(max_length=1024, blank=True, null=True)
    state_house_district = models.IntegerField(blank=True, null=True)
    state_senate_district = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gunviolence_origin'


class GunviolenceParticipant(models.Model):
    name = models.CharField(max_length=64)
    age = models.PositiveSmallIntegerField()
    gender = models.PositiveSmallIntegerField()
    harm = models.PositiveSmallIntegerField()
    type = models.PositiveSmallIntegerField()
    relationship = models.PositiveSmallIntegerField(blank=True, null=True)
    involve = models.ForeignKey(GunviolenceGunviolence, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'gunviolence_participant'


