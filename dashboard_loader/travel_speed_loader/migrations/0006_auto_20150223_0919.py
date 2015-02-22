# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):
    dependencies = [
        ('travel_speed_loader', '0005_auto_20150220_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='road',
            name='am_direction',
            field=models.CharField(max_length=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='road',
            name='pm_direction',
            field=models.CharField(max_length=2),
            preserve_default=True,
        ),
    ]
