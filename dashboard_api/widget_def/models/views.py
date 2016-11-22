#   Copyright 2016 CSIRO
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
    """
    A type of :model:`widget_def.WidgetView`

    Typically used by the front end implementation to choose the appropriate display template for a WidgetView.
    """
    name = models.CharField(max_length=120, unique=True, help_text="The name of the view type, as it appears in the API")
    show_children = models.BooleanField(default=False, help_text="If true views of this type should show links to their child views")
    show_siblings = models.BooleanField(default=False, help_text="If true views of this type should show links to their sibling views")
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
    """
    A WidgetView is a collection of widgets to be displayed at once - a dashboard in a hierarchical family of dashboards.
    """
    name = models.CharField(max_length=120, help_text="The display name for the view, as displayed in links to the view, and in the view itself")
    label = models.SlugField(unique=True, help_text="The symbolic label for the view, as used in the API.")
    parent = models.ForeignKey("self", null=True,blank=True, related_name="children", help_text="The parent WidgetView. If null, this WidgetView is a root node in a view hierarchy.")
    external_url = models.URLField(null=True, blank=True, help_text="If not null, then this Widget View is not hosted locally, but is merely a placeholder for a view hosted by another Openboard instance, and this is the API root URL for that external Openboard instance.")
    view_type = models.ForeignKey(ViewType, help_text="The type of WidgetView")
    sort_order = models.IntegerField(help_text="WidgetViews are sorted by parent, then by this field")
    requires_authentication = models.BooleanField(default=False, help_text="If true then authentication is required to access this view. Note that authentication is not supported across externally hosted WidgetViews.")
    geo_window = models.ForeignKey("GeoWindow", null=True, blank=True, help_text="A geospatial window - a rectangle that defines the initial viewing area for geodatasets under this WidgetView.  A WidgetView with a non-null geowindow may contain GeoDatasets as well as widgets.")
    class Meta:
        unique_together=[
            ("parent", "name"),
            ("parent", "sort_order"),
        ]
        ordering=["parent__label", "sort_order"]
    def save(self, *args, **kwargs):
        if self.external_url == "":
            self.external_url = None
        super(WidgetView, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.label
    def desc(self):
        desc =  {
            "name": self.name,
            "label": self.label,
        }
        if self.external_url:
            desc["api_url_base"] = self.external_url
        return desc
    def crumbs(self):
        c = []
        v = self
        while v:
            c.append(v.desc())
            v = v.parent
        c.reverse() 
        return c
    def properties(self):
        return { vp.key: vp.value() for vp in self.viewproperty_set.all() }
    def __getstate__(self):
        data = {
            "crumbs": self.crumbs(),
            "type": self.view_type.name,
            "label": self.label,
            "name": self.name,
            "show_children": self.view_type.show_children,
            "show_siblings": self.view_type.show_siblings,
            "properties": { p.key: p.value() for p in self.viewproperty_set.all() },
            "widgets": [ decl.__getstate__() for decl in self.widgets.all() ], 
        }
        other_menus = []
        for vfm in self.viewfamilymember_set.order_by("family"):
            other_menus.append(vfm.family.__getstate__(self))
        if other_menus:
            data["other_menus"] = other_menus
        if self.view_type.show_children:
            data["children"] = [ c.desc() for c in self.children.all() ]
        if self.view_type.show_siblings:
            if self.parent:
                data["siblings"] = [ c.desc() for c in self.parent.children.exclude(id=self.id) ]
            else:
                data["siblings"] = [ c.desc() for c in WidgetView.objects.filter(parent__isnull=True) ]
        return data
    def export(self):
        data = {
            "name": self.name,
            "label": self.label,
            "view_type": self.view_type.export(),
            "sort_order": self.sort_order,
            "external_url": self.external_url,
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
        v.external_url = data.get("external_url")
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
    """
    Views can have arbitrary key-value properties which can be used by front-end implementations for
    any purpose.  View properties also support :model:`widget_def.Parametisation`
    """
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
    view=models.ForeignKey(WidgetView, help_text="The view this property belongs to")
    key=models.CharField(max_length=120, help_text="The key for this property")
    property_type=models.SmallIntegerField(choices=property_types.items(), help_text="The datatype of this property")
    strval=models.TextField(blank=True, null=True, help_text="The value (for string properties)")
    intval=models.IntegerField(blank=True, null=True, help_text="The value (for integer properties)")
    boolval=models.NullBooleanField(help_text="The value (for boolean properties)")
    decval=models.DecimalField(decimal_places=4, max_digits=14, blank=True, null=True, help_text="The value (for decimal properties)")
    def value(self):
        """Return the appropriately typed value for this property"""
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

class ViewFamily(models.Model):
    """
    A ViewFamily is a set of :model:`widget_def.WidgetView`s that are related across hierarchical boundaries.

    They are used to represent secondary menus that may cut across the main view hierarchy.
    """
    name = models.CharField(max_length=120, null=True, blank=True, help_text="The display name for the secondary menu")
    label = models.SlugField(unique=True, help_text="The symbolic label for the view, as used in the API.")
    sort_order = models.IntegerField(unique=True, help_text="The secondary menus for a view are sorted by this field")
    class Meta:
        ordering = ('sort_order', )
    def __unicode__(self):
        return "ViewFamily %s" % self.label
    def export(self):
        return {
            "name": self.name,
            "family": self.label,
            "sort_order": self.sort_order,
            "members": [ fm.export() for fm in self.viewfamilymember_set.all() ],
        }
    @classmethod
    def import_data(cls, data):
        fam, created = ViewFamily.objects.get_or_create(label=data["family"], defaults={"name": data["name"], "sort_order": data["sort_order"]})
        members = []
        for m in data["members"]:
            vfm = ViewFamilyMember.import_data(fam, m)
            members.append(vfm.view.label)
        for vfm in fam.viewfamilymember_set.all():
            if vfm.view.label not in members:
                vfm.delete()
        return fam
    def __getstate__(self, enclosing_view):
        return {
            "name": self.name,
            "members": [ vfm.__getstate__(enclosing_view) for vfm in self.viewfamilymember_set.all() ]
        }

class ViewFamilyMember(models.Model):
    """
    Marks a :model:`widget_def.WidgetView` as belonging to a :model:`widget_def.ViewFamily`.
    """
    family = models.ForeignKey(ViewFamily, help_text="The family belonged to")
    view = models.ForeignKey(WidgetView, help_text="The view belonging to")
    name = models.CharField(max_length=120, help_text="How this view is labeled in the family menu.")
    sort_order = models.IntegerField(help_text="How the views are sorted within the family")
    class Meta:
        unique_together=[
            ('family', 'view'),
            ('family', 'name'),
            ('family', 'sort_order'),
        ]
        ordering= ('family', 'sort_order')
    def __unicode__(self):
        return "%s (%s)" % (self.family.label, self.name)
    def export(self):
        return { 
            "view": self.view.label,
            "name": self.name,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, family, data):
        view = WidgetView.objects.get(label=data["view"])
        vfm, created = cls.objects.get_or_create(view=view, family=family, defaults={"name": data["name"], "sort_order": data["sort_order"] })
        return vfm
    def __getstate__(self, from_view):
        if from_view == self.view:
            return {
                "menu_entry": self.name,
                "view": "self",
            }
        else:
            return {
                "menu_entry": self.name,
                "view": self.view.desc(),
            }

