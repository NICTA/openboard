# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_social_media_cat(apps, schema_editor):
    Category = apps.get_model("widget_def", "Category")
    Subcategory = apps.get_model("widget_def", "Subcategory")
    try:
        cat = Category.objects.get(name="Social Media")
    except Category.DoesNotExist:
        cat = Category(name="Social Media", sort_order=350)
        cat.save()
    try:
        sub = Subcategory.objects.get(category=cat, name="Twitter")
    except Subcategory.DoesNotExist:
        sub = Subcategory(category=cat, name="Twitter")
    sub.sort_order=15
    sub.save()


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0037_auto_20150325_1544'),
    ]

    operations = [
        migrations.RunPython(add_social_media_cat),
    ]
