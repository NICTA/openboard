# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-10 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skills_cert3_uploader', '0003_skillscert3data_rse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skillscert3data',
            options={'ordering': ('year', 'state')},
        ),
    ]
