# Generated by Django 3.0.4 on 2020-03-31 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20200331_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='configs',
            name='daemon_status',
            field=models.CharField(default='Неизвестно', max_length=255, verbose_name='Статус сервиса'),
        ),
    ]