# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_or_update_frequencies(apps, schema_editor):
    Frequency = apps.get_model("widget_def", "Frequency")
    try:
        f = Frequency.objects.get(url="rt")
    except Frequency.DoesNotExist:
        f = Frequency(url="rt")
    f.name = "Current"
    f.sort_order=100
    f.display_mode=True
    f.actual_display='Real time'
    f.save()
    try:
        f = Frequency.objects.get(url="hour")
    except Frequency.DoesNotExist:
        f = Frequency(url="hour")
    f.name = "Hourly"
    f.sort_order=200
    f.display_mode=False
    f.actual_display='Hourly'
    f.save()
    try:
        f = Frequency.objects.get(url="day")
    except Frequency.DoesNotExist:
        f = Frequency(url="day")
    f.name = "Daily"
    f.sort_order=300
    f.display_mode=False
    f.actual_display='Daily'
    f.save()
    try:
        f = Frequency.objects.get(url="week")
    except Frequency.DoesNotExist:
        f = Frequency(url="week")
    f.name = "Weekly"
    f.sort_order=400
    f.display_mode=False
    f.actual_display='Weekly'
    f.save()
    try:
        f = Frequency.objects.get(url="month")
    except Frequency.DoesNotExist:
        f = Frequency(url="month")
    f.name = "Monthly"
    f.sort_order=500
    f.display_mode=False
    f.actual_display='Monthly'
    f.save()
    try:
        f = Frequency.objects.get(url="year")
    except Frequency.DoesNotExist:
        f = Frequency(url="year")
    f.name = "Yearly"
    f.sort_order=600
    f.display_mode=False
    f.actual_display='Annual'
    f.save()

def create_or_update_locations(apps, schema_editor):
    Location = apps.get_model("widget_def", "Location")
    try:
        l = Location.objects.get(url="syd")
    except Location.DoesNotExist:
        l = Location(url="syd")
    l.name = "Sydney"
    l.sort_order=100
    l.save()
    try:
        l = Location.objects.get(url="nsw")
    except Location.DoesNotExist:
        l = Location(url="nsw")
    l.name = "New South Wales"
    l.sort_order=200
    l.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0015_frequency_actual_display'),
    ]

    operations = [
        migrations.RunPython(create_or_update_frequencies),
        migrations.RunPython(create_or_update_locations),
    ]
