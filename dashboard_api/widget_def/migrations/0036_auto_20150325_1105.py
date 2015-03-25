# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_market_subcat(apps, schema_editor):
    Category = apps.get_model("widget_def", "Category")
    Subcategory = apps.get_model("widget_def", "Subcategory")
    try:
        cat = Category.objects.get(name="Economic")
    except Category.DoesNotExist:
        cat = Category(name="Economic", sort_order=400)
        cat.save()
    try:
        subcat = Subcategory.objects.get(category=cat, name="Market")
    except Subcategory.DoesNotExist:
        subcat = Subcategory(category=cat, name="Market")
    subcat.sort_order=100
    subcat.save()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0035_widgetfamily_source_url_text'),
    ]

    operations = [
        migrations.RunPython(add_market_subcat),
    ]
