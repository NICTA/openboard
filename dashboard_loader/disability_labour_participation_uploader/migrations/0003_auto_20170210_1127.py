# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-10 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disability_labour_participation_uploader', '0002_disabilitylabourparticipation_rse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='disabilitylabourparticipation',
            options={'ordering': ('year', 'state')},
        ),
    ]
