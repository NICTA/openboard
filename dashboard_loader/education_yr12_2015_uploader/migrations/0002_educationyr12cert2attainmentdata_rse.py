# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-30 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_yr12_2015_uploader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationyr12cert2attainmentdata',
            name='rse',
            field=models.DecimalField(decimal_places=1, default=1.0, max_digits=3),
            preserve_default=False,
        ),
    ]
