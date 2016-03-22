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

from widget_def.models import ViewProperty as RealViewProperty
    
def get_create_vt(apps, name, show_children):
    ViewType=apps.get_model("widget_def", "ViewType")
    try:
        return ViewType.objects.get(name=name)
    except ViewType.DoesNotExist:
        vt = ViewType(name=name, show_children=show_children)
        vt.save()
        return vt

def get_mindex_vt(apps):
    return get_create_vt(apps, "Migrated Index View", True)

def get_mview_vt(apps):
    return get_create_vt(apps, "Migrated View", False)

def get_sort_order(_model, **kwargs):
    last = _model.objects.filter(**kwargs).last()
    if last:
        return last.sort_order + 10
    else:
        return 10

def get_create_view(apps,
        vtype,
        label,
        name,
        parent=None,
        requires_authentication=False,
        geo_window=None,
        str_properties={}
        ): 
    WidgetView=apps.get_model("widget_def", "WidgetView")
    ViewProperty=apps.get_model("widget_def", "ViewProperty")
    try:
        return WidgetView.objects.get(label=label)
    except WidgetView.DoesNotExist:
        v = WidgetView(name=name,
                        label=label,
                        parent=parent,
                        view_type=vtype,
                        requires_authentication=requires_authentication,
                        geo_window=geo_window,
                        sort_order=get_sort_order(WidgetView, parent=parent))
        v.save()
        for (prop_name, prop_val) in str_properties.items():
            prop = ViewProperty(view=v, key=prop_name,
                            property_type=RealViewProperty.STR_PROPERTY,
                            strval=prop_val)
            prop.save()
        return v

def migrate_declaration(wd, apps):
    ViewWidgetDeclaration=apps.get_model("widget_def", "ViewWidgetDeclaration")
    theme_view = get_create_view(apps,
                vtype=get_mindex_vt(apps),
                label="t%s_migration" % wd.theme.url,
                name=wd.theme.name,
                requires_authentication=wd.theme.requires_authentication,
                str_properties={
                    "theme": wd.theme.name,
                })
    freq_view = get_create_view(apps,
                vtype=get_mindex_vt(apps),
                label="t%s_f%s_migration" % (wd.theme.url, wd.frequency.url),
                name=wd.frequency.name,
                parent=theme_view,
                requires_authentication=wd.theme.requires_authentication,
                str_properties={
                    "theme": wd.theme.name,
                    "frequency": wd.frequency.name,
                })
    view = get_create_view(apps,
                vtype=get_mview_vt(apps),
                label="t%s_f%s_l%s_migration" % (wd.theme.url, wd.frequency.url, wd.location.url),
                name=wd.location.name,
                parent=freq_view,
                geo_window=wd.location.geo_window,
                requires_authentication=wd.theme.requires_authentication,
                str_properties={
                    "theme": wd.theme.name,
                    "frequency": wd.frequency.name,
                    "location": wd.location.name,
                })
    try:
        vwd=ViewWidgetDeclaration.objects.get(view=view, definition=wd.definition)
    except ViewWidgetDeclaration.DoesNotExist:
        vwd=ViewWidgetDeclaration(definition=wd.definition,
                                view=view,
                                sort_order=get_sort_order(ViewWidgetDeclaration, view=view))
        vwd.save()

def migrate_declarations(apps, schema_editor):
    WidgetDeclaration=apps.get_model("widget_def", "WidgetDeclaration")
    for wd in WidgetDeclaration.objects.all():
        migrate_declaration(wd, apps)

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0043_auto_20160321_1531'),
    ]

    operations = [
        migrations.RunPython(migrate_declarations),
    ]
