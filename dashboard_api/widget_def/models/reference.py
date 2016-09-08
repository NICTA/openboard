#   Copyright 2015,2016 NICTA
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

import decimal

from django.db import models
from django.apps import apps

# Create your models here.

class Category(models.Model):
    """
    Widgets may be organised into categories.

    Widgets within a view are sorted by category (and subcategory).

    Front end implementations may use category to influence display -  e.g.
    the category (and subcategory) of a widget may determine the colour
    pallet used for the widget, the fixed column the widget should be
    placed in, or other display properties.
    """
    name = models.CharField(max_length=60, unique=True, help_text="The category name, as it appears in API.")
    category_aspect = models.IntegerField(help_text="A numeric value associated with the category, the interpretation may vary between front end implementations. Possible uses include relative size of widgets of this category.")
    sort_order = models.IntegerField(unique=True, help_text="Widgets are sorted by category according to the value of this field.")
    def export(self):
        """Serialise category for export"""
        return {
            "name": self.name,
            "aspect": self.category_aspect,
            "sort_order": self.sort_order,
            "subcategories": [ s.export() for s in self.subcategory_set.all() ],
        }
    @classmethod
    def import_data(cls, data, merge=False):
        """
        Import a category (as serialised by export)

        data: The serialised category to be imported.

        merge: Behaviour if category already exists.  If true, serialised 
               subcategories are merged with existing ones.  If false existing
               subcategories are deleted.
        """
        try:
            c = cls.objects.get(name=data["name"])
        except cls.DoesNotExist:
            c = cls(name=data["name"])
        c.category_aspect = data["aspect"]
        c.sort_order = data["sort_order"]
        c.save()
        subcats = []
        for s in data["subcategories"]:
            sub = Subcategory.import_data(c, s)
            subcats.append(sub.name)
        if not merge:
            for sub in c.subcategory_set.all():
                if sub.name not in subcats:
                    sub.delete()
        return c
    @classmethod
    def export_all(cls):
        """
            Export all categories at once.
        """
        return { "categories": [ c.export() for c in cls.objects.all() ] }
    def __unicode__(self):
        return self.name
    class Meta:
        ordering=("sort_order",)

class AllCategories(object):
    """
    Dummy model used by the import_export code to export all categories.
    """
    _instance = None
    def export(self):
        return Category.export_all()
    @classmethod
    def import_data(cls, data, merge=False):
        cats = []
        for c in data["categories"]:
            cat = Category.import_data(c, merge)
            cats.append(cat.name)
        if not merge:
            for cat in Category.objects.all():
                if cat.name not in cats:
                    cat.delete()
        if not cls._instance:
            cls._instance = cls() 
        return cls._instance

class Subcategory(models.Model):
    """
    A :model:`widget_def.Category` has one of more subcategories.
    
    Subcategories provide a finer classification of widgets than
    categories but otherwise serve the same purpose.
    """
    category = models.ForeignKey(Category, help_text="The parent category")
    name = models.CharField(max_length=60, help_text="The subcategory name, as it appears in the API")
    sort_order = models.IntegerField(help_text="Widgets are sorted by subcategory (after sorting by category) according to the value of this field.")
    def export(self):
        """Serialise subcategory for export"""
        return {
            "name": self.name,
            "sort_order": self.sort_order,
        }
    @classmethod
    def import_data(cls, cat, data):
        """
        Import a subcategory (as serialised by export)

        cat: The parent category to attach the new subcategory to.

        data: The serialised subcategory to be imported.
        """
        try:
            sub = cls.objects.get(category=cat, name=data["name"])
        except cls.DoesNotExist:
            sub = cls(category=cat, name=data["name"])
        sub.sort_order = data["sort_order"]
        sub.save()
        return sub
    def __unicode__(self):
        return "%s:%s" % (self.category.name, self.name)
    class Meta:
        unique_together=(('category', 'name'), ('category', 'sort_order'))
        ordering= ('category', 'sort_order')

