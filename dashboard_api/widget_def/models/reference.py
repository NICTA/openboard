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

class ViewType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    show_children = models.BooleanField(default=False)
    show_siblings = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name
    def export(self):
        return {
            "name": self.name,
            "show_children": self.show_children,
            "show_siblings": self.show_siblings
        }
    @classmethod
    def import_data(cls, data):
        try:
            vt = cls.objects.get(name=data["name"])
        except cls.DoesNotExist:
            vt = cls(name=data["name"])
        vt.show_children = data["show_children"]
        vt.show_siblings = data.get("show_siblings", False)
        vt.save()
        return vt

class WidgetView(models.Model):
    name = models.CharField(max_length=120)
    label = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True,blank=True, related_name="children")
    view_type = models.ForeignKey(ViewType)
    sort_order = models.IntegerField()
    requires_authentication = models.BooleanField(default=False)
    geo_window = models.ForeignKey("GeoWindow", null=True, blank=True)
    class Meta:
        unique_together=[
            ("parent", "name"),
            ("parent", "sort_order"),
        ]
        ordering=["sort_order"]
    def __unicode__(self):
        return self.label
    def desc(self):
        return {
            "name": self.name,
            "label": self.label,
        }
    def crumbs(self):
        c = []
        v = self
        while v:
            c.append(v.desc())
            v = v.parent
        c.reverse() 
        return c
    def __getstate__(self):
        data = {
            "crumbs": self.crumbs(),
            "type": self.view_type.name,
            "show_children": self.view_type.show_children,
            "show_siblings": self.view_type.show_siblings,
            "properties": { p.key: p.value() for p in self.viewproperty_set.all() },
            "widgets": [ decl.__getstate__() for decl in self.widgets.all() ], 
        }
        if self.view_type.show_children:
            data["children"] = [ c.desc() for c in self.children.all() ]
        if self.view_type.show_siblings:
            if self.parent:
                data["siblings"] = [ c.desc() for c in self.parent.children.exclude(id=self.id) ]
            else:
                data["siblings"] = []
        return data
    def export(self):
        data = {
            "name": self.name,
            "label": self.label,
            "view_type": self.view_type.export(),
            "sort_order": self.sort_order,
            "requires_authentication": self.requires_authentication,
            "properties": [ p.export() for p in self.viewproperty_set.all() ],
            "children": [ c.export() for c in self.children.all() ],
        }
        if self.geo_window:
            data["geo_window"] = self.geo_window.name
        return data
    @classmethod
    def import_data(cls, data, parent=None):
        try:
            v = cls.objects.get(label=data["label"])
        except cls.DoesNotExist:
            v = cls(label=data["label"])
        v.parent = parent
        v.name = data["name"]
        v.view_type = ViewType.import_data(data["view_type"])
        v.sort_order = data["sort_order"]
        v.requires_authentication = data["requires_authentication"]
        if "geo_window" in data:
            GeoWindow = apps.get_app_config("widget_def").get_model("GeoWindow")
            v.geo_window = GeoWindow.objects.get(name=data["geo_window"])
        else:
            v.geo_window = None
        v.save()
        # properties
        v.viewproperty_set.all().delete()
        for p in data["properties"]:
            ViewProperty.import_data(v, p)
        # children
        children_loaded = []
        for c in data["children"]:
            cl = cls.import_data(c, parent=v) 
            children_loaded.append(cl.label)
        for c in v.children.all():
            if c.label not in children_loaded:
                c.delete()
        return v

class ViewProperty(models.Model):
    INT_PROPERTY=0
    STR_PROPERTY=1
    BOOL_PROPERTY=2
    DEC_PROPERTY=3
    property_types={
        INT_PROPERTY: "integer",
        STR_PROPERTY: "string",
        BOOL_PROPERTY: "boolean",
        DEC_PROPERTY: "decimal",
    }
    view=models.ForeignKey(WidgetView)
    key=models.CharField(max_length=120)
    property_type=models.SmallIntegerField(choices=property_types.items())
    strval=models.CharField(max_length=255, blank=True, null=True)
    intval=models.IntegerField(blank=True, null=True)
    boolval=models.NullBooleanField()
    decval=models.DecimalField(decimal_places=4, max_digits=14, blank=True, null=True)
    def value(self):
        if self.property_type == self.INT_PROPERTY:
            return self.intval
        elif self.property_type == self.DEC_PROPERTY:
            return self.decval
        elif self.property_type == self.BOOL_PROPERTY:
            return self.boolval
        else:
            return self.strval
    def save(self, *args, **kwargs):
        if self.property_type == self.INT_PROPERTY:
            if self.intval is None:
                raise Exception("Must set integer value on an integer property")
        else:
            self.intval = None
        if self.property_type == self.DEC_PROPERTY:
            if self.decval is None:
                raise Exception("Must set decimal value on an decimal property")
        else:
            self.decval = None
        if self.property_type == self.BOOL_PROPERTY:
            if self.boolval is None:
                raise Exception("Must set boolean value on an boolean property")
        else:
            self.boolval = None
        if self.property_type == self.STR_PROPERTY:
            if self.strval is None:
                raise Exception("Must set string value on an string property")
        else:
            self.strval = None
        super(ViewProperty, self).save(*args, **kwargs)
    def __unicode__(self):
        return "%s: %s" % (self.key, unicode(self.value()))
    class Meta:
        unique_together=[ ("view", "key") ]
    def export(self):
        data = {
            "key": self.key,
            "type": self.property_type,
        }
        if self.property_type == self.INT_PROPERTY:
            data["value"] = self.intval
        elif self.property_type == self.BOOL_PROPERTY:
            data["value"] = self.boolval
        else:
            data["value"] = unicode(self.value())
        return data
    @classmethod
    def import_data(cls, view, data):
        try:
            vp = cls.objects.get(view=view, key=data["key"])
        except cls.DoesNotExist:
            vp = cls(view=view, key=data["key"])
        vp.property_type = data["type"]
        if vp.property_type == cls.INT_PROPERTY:
            vp.intval = data["value"]
        elif vp.property_type == cls.BOOL_PROPERTY:
            vp.boolval = data["value"]
        elif vp.property_type == cls.DEC_PROPERTY:
            vp.decval = decimal.Decimal(data["value"])
        else:
            vp.strval = data["value"]
        vp.save()
        return vp

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

