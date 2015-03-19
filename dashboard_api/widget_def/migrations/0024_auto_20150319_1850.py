# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_families(apps, schema_editor):
    WidgetFamily = apps.get_model("widget_def", "WidgetFamily")
    WidgetDefinition = apps.get_model("widget_def", "WidgetDefinition")
    for wd in WidgetDefinition.objects.all():
        try:
            family = WidgetFamily.objects.get(url=wd.url)
        except WidgetFamily.DoesNotExist:
            family = WidgetFamily(url=wd.url)
        if family.name and family.name != wd.name:
            print "Name mismatch!  %s -> %s" % (family.name, wd.name)
        family.name = wd.name
        if family.subcategory_id and family.subcategory.id != wd.subcategory.id:
            print "Subcategory mismatch!  %s -> %s" % (unicode(family.subcategory), unicode(wd.subcategory))
        family.subcategory = wd.subcategory
        if family.source_url and family.source_url != wd.source_url:
            print "Source URL mismatch!  %s -> %s" % (family.source_url, wd.source_url)
        family.source_url = wd.source_url
        family.save()
        wd.family = family
        wd.save()


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0023_auto_20150319_1850'),
    ]

    operations = [
        migrations.RunPython(create_families),
    ]
