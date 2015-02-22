# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel_speed_loader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roadsection',
            name='label',
            field=models.CharField(max_length=10),
            preserve_default=True,
        ),
    ]
