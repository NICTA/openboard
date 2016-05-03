# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_rds_name(apps, schema_editor):
    RawDataSet = apps.get_model("widget_def", "RawDataSet")
    for rds in RawDataSet.objects.all():
        rds.name = rds.url
        rds.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0052_rawdataset_name'),
    ]

    operations = [
        migrations.RunPython(set_rds_name),
    ]

