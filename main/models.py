from django.db import models


# Create your models here.

class AttackType(models.Model):
    name = models.CharField(max_length=50)


class BlackList(models.Model):
    reg = models.CharField(max_length=200)
    head = models.BooleanField()
    url = models.BooleanField()
    args = models.BooleanField()
    body = models.BooleanField()
    type = models.ForeignKey(AttackType, on_delete=models.CASCADE)
    stable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
