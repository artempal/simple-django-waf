from django.db import models


# Create your models here.

class AttackType(models.Model):
    name = models.CharField(max_length=50)


class BlackList(models.Model):
    reg = models.CharField(max_length=200)
    head = models.BooleanField(default=False)
    url = models.BooleanField(default=False)
    args = models.BooleanField(default=False)
    body = models.BooleanField(default=False)
    type = models.ForeignKey(AttackType, on_delete=models.CASCADE)
    stable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)


class Events(models.Model):
    date = models.DateTimeField('date', auto_now=True)
    type = models.ForeignKey(AttackType, on_delete=models.CASCADE)
    reg = models.CharField(max_length=255)
    location = models.CharField(max_length=25)
    url = models.CharField(max_length=255)
    args = models.TextField()
    head = models.TextField()
    body = models.TextField()
    cookie = models.TextField()
    method = models.CharField(max_length=6)
    ip = models.CharField(max_length=15)
