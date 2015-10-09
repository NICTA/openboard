# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('traffic_incident_loader', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MajorIncident',
        ),
    ]
