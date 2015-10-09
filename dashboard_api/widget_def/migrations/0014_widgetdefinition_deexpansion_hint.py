# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def set_deexpansion_hint(apps, schema_editor):
    WidgetDefinition = apps.get_model("widget_def", "WidgetDefinition")
    for wd in WidgetDefinition.objects.all():
        if wd.expansion_hint:
            wd.deexpansion_hint = "Show less"
            wd.save()

def undo_deexpansion_hint(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0013_auto_20150619_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='deexpansion_hint',
            field=models.CharField(max_length=80, null=True, blank=True),
        ),
        migrations.RunPython(set_deexpansion_hint, reverse_code=undo_deexpansion_hint),
    ]
