# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_update_categories(apps, schema_editor):
    Category = apps.get_model("widget_def", "Category")
    try:
        c = Category.objects.get(name="General")
    except Category.DoesNotExist:
        c = Category(name="General")
    c.sort_order = 10
    c.save()
    try:
        c = Category.objects.get(name="Service Delivery")
    except Category.DoesNotExist:
        c = Category(name="Service Delivery")
    c.sort_order = 100
    c.save()
    try:
        c = Category.objects.get(name__startswith="Environment")
    except Category.DoesNotExist:
        c = Category()
    c.name = "Environment and Planning"
    c.sort_order = 200
    c.save()
    try:
        c = Category.objects.get(name__startswith="Econom")
    except Category.DoesNotExist:
        c = Category()
    c.name = "Economic"
    c.sort_order = 400
    c.save()
    try:
        c = Category.objects.get(name__in=("Media","Public Safety"))
    except Category.DoesNotExist:
        c = Category()
    c.name = "Public Safety"
    c.sort_order = 300
    c.save()
    Category.objects.exclude(name__in=("General", "Service Delivery", "Environment and Planning", "Economic", "Public Safety")).delete()

def create_update_subcategories(apps, schema_editor):
    Category = apps.get_model("widget_def", "Category")
    Subcategory = apps.get_model("widget_def", "Subcategory")
    # General
    cat = Category.objects.get(name="General")
    try:
        s = Subcategory.objects.get(category=cat, name="Baseline")
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, name="Baseline")
    s.sort_order = 10
    s.save()
    Subcategory.objects.filter(category=cat).exclude(name="Baseline").delete()
    # Service Delivery
    cat = Category.objects.get(name="Service Delivery")
    try:
        s = Subcategory.objects.get(category=cat, 
                            name__in=("Transport", "Roads"))
        s.name="Roads"
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, name="Roads")
    s.sort_order=100
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, sort_order=200)
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, sort_order=200)
    s.name="Public Transport"
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, sort_order=300)
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, sort_order=300)
    s.name="Electricity"
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, sort_order=400)
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, sort_order=400)
    s.name="Service NSW"
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, sort_order=500)
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, sort_order=500)
    s.name="Health"
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, sort_order=600)
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, sort_order=600)
    s.name="Social Services"
    s.save()
    Subcategory.objects.filter(category=cat).exclude(name__in=("Roads", 
                    "Public Transport", 
                    "Electricity", 
                    "Service NSW", 
                    "Health", 
                    "Social Services")).delete()
    # Environment and Planning
    cat = Category.objects.get(name="Environment and Planning")
    try:
        s = Subcategory.objects.get(category=cat, name="Water")
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat, name="Water")
    s.sort_order = 10
    s.save()
    try:
        s = Subcategory.objects.get(category=cat, name="Warnings")
    except Subcategory.DoesNotExist:
        s = Subcategory(category=cat)
    s.name = "Environment"
    s.sort_order = 20
    s.save()
    s = Subcategory(category=cat, name="Planning", sort_order=30)
    s.save()
    Subcategory.objects.filter(category=cat).exclude(name__in=(
                        "Water", 
                        "Environment", 
                        "Planning")).delete()
    # Public Safety
    cat = Category.objects.get(name="Public Safety")
    s = Subcategory(category=cat, name="Emergency Services", sort_order=10)
    s.save()
    s = Subcategory(category=cat, name="Crime", sort_order=20)
    s.save()
    s = Subcategory(category=cat, name="Warnings", sort_order=30)
    s.save()
    Subcategory.objects.filter(category=cat).exclude(name__in=(
                        "Emergency Services", 
                        "Crime", 
                        "Warnings")).delete()
    # Economic
    cat = Category.objects.get(name="Economic")
    s = Subcategory(category=cat, name="Budgetary", sort_order=50)
    s.save()
    Subcategory.objects.filter(category=cat).exclude(name="Budgetary").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0006_auto_20150226_1651'),
    ]

    operations = [
        migrations.RunPython(create_update_categories),
        migrations.RunPython(create_update_subcategories),
    ]
