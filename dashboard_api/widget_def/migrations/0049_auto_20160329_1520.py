# -*- coding: utf-8 -*-
#
#   Copyright 2016 NICTA
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

from django.db import migrations, models

def migrate_definition_labels(apps, schema_editor):
    WidgetDefinition = apps.get_model("widget_def", "WidgetDefinition")
    for wd in WidgetDefinition.objects.all():
        wd.label = "%s:%s" % (wd.actual_location.url, wd.actual_frequency.url)
        wd.default_frequency_text = wd.actual_frequency.actual_display
        wd.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0048_auto_20160329_1528'),
    ]

    operations = [
        migrations.RunPython(migrate_definition_labels),
    ]
