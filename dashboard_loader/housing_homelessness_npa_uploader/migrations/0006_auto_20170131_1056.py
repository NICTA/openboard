# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-30 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('housing_homelessness_npa_uploader', '0005_auto_20161122_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housinghomelessnessnpaprogress',
            name='matched_funding',
            field=models.SmallIntegerField(choices=[(1, 'Completed'), (2, 'In progress'), (3, 'N/A'), (4, 'Not started')]),
        ),
        migrations.AlterField(
            model_name='housinghomelessnessnpaprogress',
            name='plan1',
            field=models.SmallIntegerField(choices=[(1, 'Completed'), (2, 'In progress'), (3, 'N/A'), (4, 'Not started')]),
        ),
        migrations.AlterField(
            model_name='housinghomelessnessnpaprogress',
            name='plan2',
            field=models.SmallIntegerField(choices=[(1, 'Completed'), (2, 'In progress'), (3, 'N/A'), (4, 'Not started')]),
        ),
        migrations.AlterField(
            model_name='housinghomelessnessnpaprogress',
            name='update',
            field=models.SmallIntegerField(choices=[(1, 'Completed'), (2, 'In progress'), (3, 'N/A'), (4, 'Not started')]),
        ),
    ]
