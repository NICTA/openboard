# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Loader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app', models.CharField(unique=True, max_length=80)),
                ('refresh_rate', models.IntegerField()),
                ('last_loaded', models.DateTimeField(null=True, blank=True)),
                ('locked_by_process', models.IntegerField(null=True, blank=True)),
                ('suspended', models.BooleanField(default=False)),
                ('last_run', models.DateTimeField(null=True, blank=True)),
                ('last_locked', models.DateTimeField(null=True, blank=True)),
                ('locked_by_thread', models.DecimalField(null=True, max_digits=19, decimal_places=0, blank=True)),
                ('last_api_access', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Uploader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app', models.CharField(unique=True, max_length=80)),
                ('last_uploaded', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]
