# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from widget_def.models import TileDefinition

def copy_list_widths(apps, schema_editor):
    MigrationTileDef = apps.get_model("widget_def", "TileDefinition")
    for t in MigrationTileDef.objects.filter(tile_type=TileDefinition.SINGLE_LIST_STAT):
        s = t.statistic_set.all()[0]
        t.list_label_width = s.list_label_width
        t.save()

def add_social_services_subcat(apps, schema_editor):
    Category = apps.get_model("widget_def", "Category")
    Subcategory = apps.get_model("widget_def", "Subcategory")
    try:
        cat = Category.objects.get(name="Public Safety")
    except Category.DoesNotExist:
        cat = Category(name="Public Safety", sort_order=300)
        cat.save()
    try:
        sub = Subcategory.objects.get(category=cat, name="Social Services")
    except Subcategory.DoesNotExist:
        sub = Subcategory(category=cat, name="Social Services")
    sub.sort_order=15
    sub.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0032_tiledefinition_list_label_width'),
    ]

    operations = [
        migrations.RunPython(copy_list_widths),
        migrations.RunPython(add_social_services_subcat),
    ]
