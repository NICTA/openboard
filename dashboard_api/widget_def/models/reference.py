#   Copyright 2015 NICTA
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

from django.db import models
from django.apps import apps

# Create your models here.

class Theme(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    requires_authentication = models.BooleanField(default=True)
    sort_order = models.IntegerField()
    def export(self):
        return {
            "name": self.name,
            "url": self.url,
            "requires_auth": self.requires_authentication,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, data):
        try:
            t = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            t = cls(url=data["url"])
        t.name = data["name"]
        t.requires_authentication = data["requires_auth"]
        t.sort_order = data["sort_order"]
        t.save()
        return t
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    geo_window = models.ForeignKey("GeoWindow", null=True, blank=True)
    sort_order = models.IntegerField()
    def export(self):
        data = {
            "name": self.name,
            "url": self.url,
            "sort_order": self.sort_order,
        }
        if self.geo_window:
            data["geo_window"] = self.geo_window.name
        return data
    @classmethod
    def import_data(cls, data):
        try:
            loc = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            loc = cls(url=data["url"])
        loc.name = data["name"]
        loc.sort_order = data["sort_order"]
        if "geo_window" in data:
            GeoWindow = apps.get_app_config("widget_def").get_model("GeoWindow")
            loc.geo_window = GeoWindow.objects.get(name=data["geo_window"])
        else:
            loc.geo_window = None
        loc.save()
        return loc
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Frequency(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    display_mode = models.BooleanField(default=True)
    actual_display = models.CharField(max_length=60, unique=True)
    sort_order = models.IntegerField()
    def export(self):
        return {
            "name": self.name,
            "url": self.url,
            "display_mode": self.display_mode,
            "actual_display": self.actual_display,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, data):
        try:
            f = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            f = cls(url=data["url"])
        f.name = data["name"]
        f.display_mode = data["display_mode"]
        f.actual_display = data["actual_display"]
        f.sort_order = data["sort_order"]
        f.save()
        return f
    def __unicode__(self):
        return self.url
    class Meta:
        verbose_name_plural = "frequencies"
        ordering=("sort_order",)
    def __getstate__(self):
        return {"name": self.name, "url": self.url}

class WidgetViews(object):
    _instance = None
    @classmethod
    def import_data(cls, data, merge=False):
        ld_fs = []
        ld_ls = []
        ld_ts = []
        #
        for d in data["frequencies"]:
            f = Frequency.import_data(d)
            ld_fs.append(f.url)
        for d in data["locations"]:
            l = Location.import_data(d)
            ld_ls.append(l.url)
        for d in data["themes"]:
            t = Theme.import_data(d)
            ld_ts.append(t.url)
        #
        if not merge:
            for f in Frequency.objects.all():
                if f.url not in ld_fs:
                    f.delete()
            for l in Location.objects.all():
                if l.url not in ld_ls:
                    l.delete()
            for t in Theme.objects.all():
                if t.url not in ld_ts:
                    t.delete()
        #
        if not cls._instance:
            cls._instance = cls() 
        return cls._instance
    def export(self):
        return {
            "frequencies": [ f.export() for f in Frequency.objects.all() ],
            "locations": [ l.export() for l in Location.objects.all() ],
            "themes": [ t.export() for t in Theme.objects.all() ],
        }

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    category_aspect = models.IntegerField()
    sort_order = models.IntegerField()
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

