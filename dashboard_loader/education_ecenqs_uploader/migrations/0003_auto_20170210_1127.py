# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-10 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('education_ecenqs_uploader', '0002_auto_20161201_1634'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationecenqsdata',
            options={'ordering': ('year', 'state')},
        ),
    ]
