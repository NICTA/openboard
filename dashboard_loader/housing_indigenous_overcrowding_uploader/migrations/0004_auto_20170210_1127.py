# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-10 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('housing_indigenous_overcrowding_uploader', '0003_indigenousovercrowdingdata_rse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indigenousovercrowdingdata',
            options={'ordering': ('year', 'state')},
        ),
    ]
