# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytz

from django.conf import settings
from django.db import models, migrations

def migrate_datekeys(apps, schema_editor):
    tz = pytz.timezone(settings.TIME_ZONE)
    StatisticListItem = apps.get_model("widget_data", "StatisticListItem")
    for si in StatisticListItem.objects.filter(datekey__isnull=False):
        si.datetime_key = tz.localize(si.datekey)
        si.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0004_auto_20150612_1142'),
    ]

    operations = [
        migrations.operations.RunPython(migrate_datekeys),
    ]
