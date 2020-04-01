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


class Configs(models.Model):
    hostname = models.CharField(max_length=255, default="127.0.0.1:81")
    port = models.IntegerField('порт', default=80)
    https = models.BooleanField('HTTPS', default=False)
    cert_file = models.CharField('Файл сертификата', default="certs/mydomain.crt", max_length=255)
    key_file = models.CharField('Ключ сертификата', default="certs/mydomain.key", max_length=255)
    strict_transport_security = models.BooleanField('добавить заголовок Strict-Transport-Security', default=False)
    x_frame_option = models.BooleanField('запрет встраивания в фреймы', default=True)
    signature_analysis = models.BooleanField('сигнатурный анализ', default=True)
    xss_browser_protection = models.BooleanField('встроенная защита браузера от XSS', default=False)
    no_sniff = models.BooleanField('запрет угадывания content-type', default=True)
    content_security_policy_self = models.BooleanField('строгая политика CSP', default=False)
    hide_server = models.BooleanField('скрытие сервера', default=True)
    hide_x_powered_by = models.BooleanField('скрытие ПО сервера', default=True)
    daemon_status = models.CharField('Статус сервиса', default='Неизвестно', max_length=255)

    class Meta:
        verbose_name = 'настройка'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return self.hostname
