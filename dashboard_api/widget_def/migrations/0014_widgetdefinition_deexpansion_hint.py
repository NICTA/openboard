# -*- coding: utf-8 -*-
#
#   Copyright 2015 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
