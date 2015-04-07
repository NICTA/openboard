# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('air_pollution_loader', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pollutionrotation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='pollutionrotation',
            name='location',
        ),
        migrations.DeleteModel(
            name='PollutionRotation',
        ),
    ]
