# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def set_actual_frequency_from_url(apps, schema_editor):
    WidgetDefinition = apps.get_model("widget_def", "WidgetDefinition")
    Frequency = apps.get_model("widget_def", "Frequency")
    for wd in WidgetDefinition.objects.all():
        f = Frequency.objects.get(url=wd.actual_frequency_url.lower())
        wd.actual_frequency = f
        wd.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0019_auto_20150319_1404'),
    ]

    operations = [
        migrations.RunPython(set_actual_frequency_from_url),
    ]
