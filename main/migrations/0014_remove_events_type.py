# Generated by Django 3.0.7 on 2020-10-28 18:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20201010_2154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='type',
        ),
    ]