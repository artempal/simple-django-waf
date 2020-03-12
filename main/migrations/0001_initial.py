# Generated by Django 3.0.4 on 2020-03-12 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttackType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg', models.CharField(max_length=200)),
                ('head', models.BooleanField()),
                ('url', models.BooleanField()),
                ('args', models.BooleanField()),
                ('body', models.BooleanField()),
                ('active', models.BooleanField(default=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.AttackType')),
            ],
        ),
    ]
