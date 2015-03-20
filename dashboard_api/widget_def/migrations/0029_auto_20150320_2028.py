# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def update_frequencies(apps, schema_editor):
    Frequency = apps.get_model("widget_def", "Frequency")
    try:
        f = Frequency.objects.get(url="year")
    except Frequency.DoesNotExist:
        f = Frequency(url="year")
    f.name = "Yearly"
    f.actual_display = "Annual"
    f.display_mode = False
    f.sort_order = 700
    f.save()
    try:
        f = Frequency.objects.get(url="quarter")
    except Frequency.DoesNotExist:
        f = Frequency(url="quarter")
    f.name = "Quarterly"
    f.actual_display = "Quarterly"
    f.display_mode = False
    f.sort_order = 600
    f.save()
    try:
        f = Frequency.objects.get(url="dummy")
    except Frequency.DoesNotExist:
        f = Frequency(url="dummy")
    f.name = "Dummy Data"
    f.actual_display = "Dummy Data"
    f.display_mode = False
    f.sort_order = 1000
    f.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0028_statistic_list_label_width'),
    ]

    operations = [
        migrations.RunPython(update_frequencies),
    ]
