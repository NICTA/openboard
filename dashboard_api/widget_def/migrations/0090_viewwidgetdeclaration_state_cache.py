# -*- coding: utf-8 -*-
#
#   Copyright 2017 CSIRO
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

def populate_widget_caches(apps, schema_editor):
    # NB This will break if we ever remove the update_state_cache method.
    from widget_def.models import ViewWidgetDeclaration
    for vwd in ViewWidgetDeclaration.objects.all():
        vwd.update_state_cache()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0089_graphdisplayoptions_pie'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewwidgetdeclaration',
            name='state_cache',
            field=models.TextField(default='', help_text=b'Cached widget json description - populated automatically, do not edit by hand.'),
            preserve_default=False,
        ),
        migrations.RunPython(populate_widget_caches),
    ]
