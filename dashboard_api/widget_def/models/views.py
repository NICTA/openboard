#   Copyright 2016,2017 CSIRO
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

class ViewType(models.Model, WidgetDefJsonMixin):
    """
    A type of :model:`widget_def.WidgetView`

    Typically used by the front end implementation to choose the appropriate display template for a WidgetView.
    """
    export_def = {
        "name": JSON_ATTR(),
        "show_children": JSON_ATTR(default=False),
        "show_siblings": JSON_ATTR(default=False),
    }
    export_lookup = { "name": "name" }
    name = models.CharField(max_length=120, unique=True, help_text="The name of the view type, as it appears in the API")
    show_children = models.BooleanField(default=False, help_text="If true views of this type should show links to their child views")
    show_siblings = models.BooleanField(default=False, help_text="If true views of this type should show links to their sibling views")
    def __unicode__(self):
        return self.name

class WidgetView(models.Model, WidgetDefJsonMixin):
    """
    A WidgetView is a collection of widgets to be displayed at once - a dashboard in a hierarchical family of dashboards.
    """
    export_def = {
        "parent": JSON_INHERITED("children", optional=True),
        "name": JSON_ATTR(),
        "label": JSON_ATTR(),
        "view_type": JSON_CAT_LOOKUP(["view_type", "export"], lambda js, k, kw: ViewType.objects.get(name=js["view_type"]["name"]), import_model=ViewType),
        "sort_order": JSON_ATTR(),
        "external_url": JSON_ATTR(),
        "requires_authentication": JSON_ATTR(),
        "geo_window": JSON_CAT_LOOKUP(["geo_window", "name"], lambda js, k, kw: apps.get_app_config("widget_def").get_model("GeoWindow").objects.get(name=js["geo_window"]), optional=True),
        "children": JSON_RECURSEDOWN("WidgetView", "children", "parent", "name", app="widget_def"),
        "properties": JSON_RECURSEDOWN("ViewProperty", "properties", "view", "key", app="widget_def")
    }
    export_lookup = { "label": "label" }
    api_state_def = {
        "crumbs": JSON_ATTR("crumbs"),
        "type": JSON_CAT_LOOKUP(["view_type", "name"], None),
        "label": JSON_ATTR(),
        "name": JSON_ATTR(),
        "show_children": JSON_CAT_LOOKUP(["view_type", "show_children"], None),
        "show_siblings": JSON_CAT_LOOKUP(["view_type", "show_siblings"], None),
        "properties": JSON_RECURSEDICT("properties", "key", "value"),
        "widgets": JSON_RECURSEDOWN("ViewWidgetDeclaration", "widgets", "view", "definition", app="widget_def"),
        "other_menus": JSON_RECURSEDOWN("ViewFamilyMember", "family_memberships", "view", "family", app="widget_def", recurse_attr_chain=["family"], recurse_obj_arg="enclosing_view", suppress_if_empty=True),
        "children": JSON_RECURSEDOWN("WidgetView", "children", "parent", "name", app="widget_def", suppress_decider="suppress_children", recurse_func_override="desc"),
        "siblings": JSON_SELF_RECURSEDOWN("WidgetView", None, None, None, app="widget_def", suppress_decider="suppress_siblings", recurse_func_override="desc")
    }
    name = models.CharField(max_length=120, help_text="The display name for the view, as displayed in links to the view, and in the view itself", unique=True)
    label = models.SlugField(unique=True, help_text="The symbolic label for the view, as used in the API.")
    parent = models.ForeignKey("self", null=True,blank=True, related_name="children", help_text="The parent WidgetView. If null, this WidgetView is a root node in a view hierarchy.")
    external_url = models.URLField(null=True, blank=True, help_text="If not null, then this Widget View is not hosted locally, but is merely a placeholder for a view hosted by another Openboard instance, and this is the API root URL for that external Openboard instance.")
    view_type = models.ForeignKey(ViewType, help_text="The type of WidgetView")
    sort_order = models.IntegerField(help_text="WidgetViews are sorted by parent, then by this field")
    requires_authentication = models.BooleanField(default=False, help_text="If true then authentication is required to access this view. Note that authentication is not supported across externally hosted WidgetViews.")
    geo_window = models.ForeignKey("GeoWindow", null=True, blank=True, help_text="A geospatial window - a rectangle that defines the initial viewing area for geodatasets under this WidgetView.  A WidgetView with a non-null geowindow may contain GeoDatasets as well as widgets.")
    def suppress_children(self):
        return not self.view_type.show_children
    def suppress_siblings(self):
        return not self.view_type.show_siblings
    class Meta:
        unique_together=[
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
    def my_properties(self):
        return { vp.key: vp.value() for vp in self.properties.all() }

def property_importer(js, cons_args, imp_kwargs):
    cons_args["intval"] = None
    cons_args["strval"] = None
    cons_args["boolval"] = None
    cons_args["decval"] = None
    if js["type"] == 0:
        cons_args["intval"] = js["value"]
    elif js["type"] == 1:
        cons_args["strval"] = js["value"]
    elif js["type"] == 2:
        cons_args["boolval"] = js["value"]
    elif js["type"] == 3:
        cons_args["decval"] = decimal.Decimal(js["value"])

class ViewProperty(models.Model, WidgetDefJsonMixin):
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
    export_def = {
        "key": JSON_ATTR(),
        "type": JSON_ATTR(attribute="property_type"),
        "value": JSON_COMPLEX_IMPORTER_ATTR(complex_importer=property_importer)
    }
    export_lookup = { "view":"view", "key":"key" }
    view=models.ForeignKey(WidgetView, related_name="properties", help_text="The view this property belongs to")
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

class ViewFamily(models.Model, WidgetDefJsonMixin):
    """
    A ViewFamily is a set of :model:`widget_def.WidgetView`s that are related across hierarchical boundaries.

    They are used to represent secondary menus that may cut across the main view hierarchy.
    """
    export_def = {
        "name": JSON_ATTR(),
        "family": JSON_ATTR(attribute="label"),
        "sort_order": JSON_ATTR(),
        "members": JSON_RECURSEDOWN("ViewFamilyMember", "members", "family", "view", app="widget_def")
    }
    export_lookup={ "family": "label" }
    api_state_def={
        "name": JSON_ATTR(),
        "members": JSON_RECURSEDOWN("ViewFamilyMember", "members", "family", "name", app="widget_def", merge=False)
    }
    name = models.CharField(max_length=120, null=True, blank=True, help_text="The display name for the secondary menu")
    label = models.SlugField(unique=True, help_text="The symbolic label for the view, as used in the API.")
    sort_order = models.IntegerField(unique=True, help_text="The secondary menus for a view are sorted by this field")
    class Meta:
        ordering = ('sort_order', )
    def __unicode__(self):
        return "ViewFamily %s" % self.label

class ViewFamilyMember(models.Model, WidgetDefJsonMixin):
    """
    Marks a :model:`widget_def.WidgetView` as belonging to a :model:`widget_def.ViewFamily`.
    """
    export_def = {
        "family": JSON_INHERITED("members"),
        "view": JSON_CAT_LOOKUP(["view", "label"],
                        lambda js, key, imp_kwargs: WidgetView.objects.get(label=js["view"])),
        "name": JSON_ATTR(),
        "sort_order": JSON_IMPLIED()
    }
    export_lookup = { "family": "family", "view": "view" }
    api_state_def = {
        "menu_entry": JSON_ATTR(attribute="name"),
        "view": JSON_CONDITIONAL_EXPORT(
                lambda obj, kwargs: kwargs["enclosing_view"] == obj.view,
                JSON_CONST(default="self"),
                JSON_CAT_LOOKUP(["view", "desc"], None)
                )
    }
    family = models.ForeignKey(ViewFamily, related_name="members", help_text="The family belonged to")
    view = models.ForeignKey(WidgetView, related_name="family_memberships", help_text="The view belonging to")
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

