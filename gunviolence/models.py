import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class State(models.Model):
    name = models.CharField(max_length=64)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()  

class City(models.Model):
    name = models.CharField(max_length=64)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()     

class IncidentCharacteristic(models.Model):
    characteristic = models.CharField(max_length=1024, choices=settings.CHARACTER_CHOICES)
    count = models.PositiveIntegerField(default=0)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

class GunViolence(models.Model):
    url = models.URLField()
    date = models.DateField()
    latitude =  models.FloatField(default=40.1020)
    longitude =  models.FloatField(default=-88.2272)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    characteristic = models.ManyToManyField(IncidentCharacteristic) 

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

class Participant(models.Model):
    name = models.CharField(max_length=64)
    age = models.PositiveSmallIntegerField()
    gender = models.PositiveSmallIntegerField(choices=settings.GENDER_CHOICES)
    harm = models.PositiveSmallIntegerField(choices=settings.HARM_CHOICES)
    type = models.PositiveSmallIntegerField(choices=settings.PTYPE_CHOICES)
    relationship = models.PositiveSmallIntegerField(choices=settings.RELATION_CHOICES, null=True, help_text="relation to all victims")
    involve = models.ForeignKey(GunViolence, on_delete=models.CASCADE)

