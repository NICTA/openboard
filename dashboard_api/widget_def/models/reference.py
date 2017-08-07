#   Copyright 2015,2016 CSIRO
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
from widget_def.model_json_tools import *


# Create your models here.

class Category(models.Model, WidgetDefJsonMixin):
    """
    Widgets may be organised into categories.

    Widgets within a view are sorted by category (and subcategory).

    Front end implementations may use category to influence display -  e.g.
    the category (and subcategory) of a widget may determine the colour
    pallet used for the widget, the fixed column the widget should be
    placed in, or other display properties.
    """
    export_def = {
         "name": JSON_ATTR(),
         "aspect": JSON_ATTR(attribute="category_aspect"),
         "sort_order": JSON_ATTR(),
         "subcategories": JSON_RECURSEDOWN("SubCategory", "subcategories", "category", "name", app="widget_def")
    }
    export_lookup = { "name": "name" }
    name = models.CharField(max_length=60, unique=True, help_text="The category name, as it appears in API.")
    category_aspect = models.IntegerField(help_text="A numeric value associated with the category, the interpretation may vary between front end implementations. Possible uses include relative size of widgets of this category.")
    sort_order = models.IntegerField(unique=True, help_text="Widgets are sorted by category according to the value of this field.")
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
            cat = Category.import_data(js=c, merge=merge)
            cats.append(cat.name)
        if not merge:
            for cat in Category.objects.all():
                if cat.name not in cats:
                    cat.delete()
        if not cls._instance:
            cls._instance = cls() 
        return cls._instance

class Subcategory(models.Model, WidgetDefJsonMixin):
    """
    A :model:`widget_def.Category` has one of more subcategories.
    
    Subcategories provide a finer classification of widgets than
    categories but otherwise serve the same purpose.
    """
    export_def = {
        "category": JSON_INHERITED("subcategories"),
        "name": JSON_ATTR(),
        "sort_order": JSON_ATTR(),
    }
    export_lookup = { "category": "category", "name": "name" }
    category = models.ForeignKey(Category, related_name="subcategories", help_text="The parent category")
    name = models.CharField(max_length=60, help_text="The subcategory name, as it appears in the API")
    sort_order = models.IntegerField(help_text="Widgets are sorted by subcategory (after sorting by category) according to the value of this field.")
    def __unicode__(self):
        return "%s:%s" % (self.category.name, self.name)
    class Meta:
        unique_together=(('category', 'name'), ('category', 'sort_order'))
        ordering= ('category', 'sort_order')

