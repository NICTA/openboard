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

from dashboard_api.migration_utils import *

def migrate_declaration(gd, apps):
    ViewGeoDatasetDeclaration=apps.get_model("widget_def", "ViewGeoDatasetDeclaration")
    view = migrate_view(apps, gd.theme, gd.frequency, gd.location)
    try:
        vwd=ViewGeoDatasetDeclaration.objects.get(view=view, definition=wd.definition)
    except ViewGeoDatasetDeclaration.DoesNotExist:
        vwd=ViewGeodatasetDeclaration(definition=gd.definition,
                                view=view,
                                sort_order=get_sort_order(ViewGeoDatasetDeclaration, view=view))
        vwd.save()

def migrate_geodeclarations(apps, schema_editor):
    GeoDatasetDeclaration=apps.get_model("widget_def", "GeoDatasetDeclaration")
    for gd in GeoDatasetDeclaration.objects.all():
        migrate_geodeclaration(gd, apps)

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0046_auto_20160323_1208'),
    ]

    operations = [
          migrations.RunPython(migrate_geodeclarations),
    ]
