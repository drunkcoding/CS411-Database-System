import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class State(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()  

class City(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    population = models.PositiveIntegerField()
    land_area = models.FloatField()     

class Location(models.Model):
    latitude =  models.FloatField(default=40.1020)
    longitude =  models.FloatField(default=-88.2272)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    
    class Meta:
        unique_together = (("latitude", "longitude"),)

class IncidentCharacteristic(models.Model):
    characteristic = models.CharField(max_length=1024, choices=settings.CHARACTER_CHOICES)
    count = models.PositiveIntegerField(default=0)
    state = models.ManyToManyField(State)
    city = models.ManyToManyField(City)

class UserProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    threshold = models.FloatField(default=1.0)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

class GunViolence(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    url = models.URLField()
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    note = models.CharField(max_length=1024, null=True)
    characteristic = models.ManyToManyField(IncidentCharacteristic) 

class Participant(models.Model):
    name = models.CharField(max_length=64)
    age = models.PositiveSmallIntegerField()
    gender = models.PositiveSmallIntegerField(choices=settings.GENDER_CHOICES)
    harm = models.PositiveSmallIntegerField(choices=settings.HARM_CHOICES)
    type = models.PositiveSmallIntegerField(choices=settings.PTYPE_CHOICES)
    relationship = models.PositiveSmallIntegerField(choices=settings.RELATION_CHOICES, null=True, help_text="relation to all victims")
    involve = models.ForeignKey(GunViolence, on_delete=models.CASCADE)

