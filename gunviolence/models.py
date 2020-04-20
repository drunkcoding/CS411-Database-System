import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class State(models.Model):
    name = models.CharField(primary_key=True, max_length=64)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()

class City(models.Model):
    name = models.CharField(max_length=64)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, to_field='name')

class GunViolence(models.Model):
    id = models.IntegerField(primary_key=True)
    #url = models.CharField(max_length=200)
    date = models.DateField()
    city = models.CharField(max_length=64)
    latitude = models.FloatField()
    longitude = models.FloatField()
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, to_field='name')
    address = models.TextField(null=True)
    #created_at = models.DateTimeField()
    #updated_at = models.DateTimeField()
    congressional_district = models.CharField(max_length=64, null=True)
    state_house_district = models.CharField(max_length=64, null=True)
    state_senate_district = models.CharField(max_length=64, null=True)

    n_killed = models.PositiveSmallIntegerField(null=True)
    n_injured = models.PositiveSmallIntegerField(null=True)
    participants = models.TextField(null=True)
    characteristics = models.TextField(null=True)
    guns = models.TextField(null=True)

    """
    class Meta:
        managed = False
        db_table = 'gunviolence_gunviolence'
    """
"""
class Characteristic(models.Model):
    incident_id = models.ForeignKey(GunViolence, on_delete=models.DO_NOTHING)
    characteristic = models.CharField(max_length=512)
"""
class Gun(models.Model):
    incident_id = models.ForeignKey(GunViolence, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=64)
    stolen = models.CharField(max_length=64)

"""
class IncidentCharacteristic(models.Model):
    characteristic = models.CharField(primary_key=True, max_length=1024)
    count = models.PositiveIntegerField()
    city = models.CharField(max_length=64)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, db_column='name')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'gunviolence_incidentcharacteristic'
"""

class Participant(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=64, blank=True, null=True)
    relationship = models.CharField(max_length=64, blank=True, null=True)
    incident = models.ForeignKey(GunViolence, on_delete=models.DO_NOTHING)
    #created_at = models.DateTimeField()
    #updated_at = models.DateTimeField()

    """
    class Meta:
        managed = False
        db_table = 'gunviolence_participant'
    """

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
    congressional_district = models.CharField(max_length=64, null=True)
    state_house_district = models.CharField(max_length=64, null=True)
    state_senate_district = models.CharField(max_length=64, null=True)
