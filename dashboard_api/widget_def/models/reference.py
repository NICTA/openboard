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
    name = models.CharField(max_length=60, unique=True)
    category_aspect = models.IntegerField()
    sort_order = models.IntegerField(unique=True)
    def export(self):
        return {
            "name": self.name,
            "aspect": self.category_aspect,
            "sort_order": self.sort_order,
            "subcategories": [ s.export() for s in self.subcategory_set.all() ],
        }
    @classmethod
    def import_data(cls, data, merge=False):
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
        return { "categories": [ c.export() for c in cls.objects.all() ] }
    def __unicode__(self):
        return self.name
    class Meta:
        ordering=("sort_order",)

class AllCategories(object):
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
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=60)
    sort_order = models.IntegerField()
    def export(self):
        return {
            "name": self.name,
            "sort_order": self.sort_order,
        }
    @classmethod
    def import_data(cls, cat, data):
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

