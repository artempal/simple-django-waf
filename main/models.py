from django.db import models


# Create your models here.

class AttackType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'атака'
        verbose_name_plural = 'Названия атак'

    def __str__(self):
        return self.name


class BlackList(models.Model):
    reg = models.CharField('Регулярное выражение', max_length=200)
    head = models.BooleanField(default=False)
    url = models.BooleanField(default=False)
    args = models.BooleanField(default=False)
    body = models.BooleanField(default=False)
    type = models.ForeignKey(AttackType, on_delete=models.CASCADE)
    stable = models.BooleanField('Точная строка', default=True)
    active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'правило'
        verbose_name_plural = 'Список правил'

    def __str__(self):
        return self.reg


class Events(models.Model):
    date = models.DateTimeField('Дата', auto_now=True)
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

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.url
