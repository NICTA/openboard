# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel_speed_loader', '0004_auto_20150218_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='road',
            name='am_direction',
            field=models.CharField(default='N', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='road',
            name='pm_direction',
            field=models.CharField(default='S', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='roadsection',
            name='route_direction',
            field=models.CharField(max_length=1),
            preserve_default=True,
        ),
    ]
