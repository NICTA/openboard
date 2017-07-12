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

from django.db import models
from widget_def.model_json_tools import *
from widget_def.models.views import WidgetView, ViewProperty

# Create your models here.

class ViewDoesNotHaveAllKeys(Exception):
    pass

class Parametisation(models.Model, WidgetDefJsonMixin):
    """
    A :model:`widget_def.WidgetDefinition` may be parametised by associating it with a Parametisation.

    A Parametisation provides a method by which the appearance and data for a widget can vary depending on the
    :model:`widget_def.WidgetView` in which it is being displayed. This means that in a situation where a (potentially
    large) group of WidgetViews might all contain a similar but slightly different widget, the widget need only
    be defined once, with the differences between the various parametised widgets being captured in the values of
    various :model:`WidgetProperty` instances.

    Many fields in widget_def objects are documented with "May be parametised" in the help_text. When
    a widget is parametised, these fields are interpreted as a Django template, with the actual value 
    within a particular view determined by rendering the template with a Context equal to the view's
    properties.
    """
    export_def = {
        "url": JSON_ATTR(),
        "name": JSON_ATTR(),
        "keys": JSON_RECURSEDOWN("ParametisationKey", "pkeys", "param", "key", app="widget_def")
    }
    export_lookup = { "url": "url" }
    url=models.SlugField(unique=True, help_text="A short symbolic name used by export commands")
    name=models.CharField(max_length=128, unique=True, help_text="A longer descriptive name.")
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)
    def export(self):
        return {
            "url": self.url,
            "name": self.name,
            "keys": self.keys(),
        }
    def add_key(self, key):
        """Add a new :model:`ParametisationKey` to this Parametisation if it does not already exist. Returns the key either way."""
        return ParametisationKey.objects.get_or_create(param=self, key=key)[0]
    def delete_key(self, key):
        """Deletes a :model:`ParametisationKey` from this Parametisation if it exists. Fails silently if it does not."""
        try:
            ParametisationKey.objects.get(param=self, key=key).delete()
        except ParametisationKey.DoesNotExist:
            pass
    def keys(self):
        """Returns this Parametisation's keys (as a list of strings)"""
        return [ pk.key for pk in self.pkeys.all() ]
    def update(self, view=None):
        """
        Update :model:`ParametisationValue` objects for this Parametisation. For specified view or all views.
        
        Should be called automatically by signals, should not need to be invoked manually.
        """
        if not view:
            for v in WidgetView.objects.all():
                self.update(v)
            for pv in self.parametisationvalue_set.all():
                if pv.views.count() == 0:
                    pv.delete()
            return
        if view.widgets.filter(definition__parametisation=self).count() == 0:
            # This view has no declared widgets for this parametisation, so remove any
            # pvals for this parametisation and view, and cleanup any resulting unused pvals,
            # and bail.
            for pv in view.parametisationvalue_set.filter(param=self):
                pv.views.remove(view)
                if pv.views.count() == 0:
                    pv.delete()
            return
        keys = self.keys()
        if view.viewproperty_set.filter(key__in=keys).count() < len(keys):
            # View does not have properties for all of this Parametisation's keys:
            # Remove any pvals for this Parametisation and View.  Cleanup any resulting unused pvals.
            for pv in view.parametisationvalue_set.filter(param=self):
                pv.views.remove(view)
                if pv.views.count() == 0:
                    pv.delete()
            return
        try:
            # Get existing pval for this param and view.
            pv = view.parametisationvalue_set.get(param=self)
        except ParametisationValue.DoesNotExist:
            # Doesn't have one yet.
            # Check if any existing pvals match.
            for pv in self.parametisationvalue_set.all():
                if pv.matches(view):
                    # Match find, attach the view and exist.
                    pv.views.add(view)
                    return
            # Create one with no parameters
            pv = ParametisationValue(param=self)
            pv.save()
            pv.views.add(view)
        # OK, so we have a view and a pval which may or may not match.
        pv_params = pv.parameters()
        v_params  = view.properties()
        for key in keys:
            if key not in pv_params:
                # pval doesn't have the key. Better add it in then!
                prop = view.viewproperty_set.get(key=key)
                pkv = ParameterValue(
                        pv=pv,
                        key=prop.key,
                        property_type=prop.property_type,
                        intval=prop.intval,
                        decval=prop.decval,
                        strval=prop.strval,
                        boolval=prop.boolval
                        )
                pkv.save()
            elif pv_params[key] != v_params[key]:
                # Both view and pval have the key - but the values don't match!
                # Remove view from pval, and delete pval if ref count is zero.
                pv.views.remove(view)
                if pv.views.count() == 0:
                    pv.delete()
                # Start again so we can create a new pval (or recycle)
                self.update(view)
                return
    @classmethod
    def update_all(cls, view=None):
        """
        Calls update on all Parametisations.
        
        Should be called automatically by signals, should not need to be invoked manually.
        """
        if not view:
            for v in WidgetView.objects.all():
                cls.update_all(v)
            return
        for p in cls.objects.all():
            p.update(view)
    @classmethod
    def import_data(cls, data):
        p = cls.objects.get_or_create(url=data["url"], name=data["name"])[0]
        for k in data["keys"]:
            p.add_key(k)
        for k in p.keys():
            if k not in data["keys"]:
                p.delete_key(k)
        p.update()
        return p
    class Meta:
        ordering = ("name",)

class ParametisationKey(models.Model, WidgetDefJsonMixin):
    """
    A key that is parametised by a :model:`Parametisation`.

    Every view that declares a widget with this Parametisation is assumed to have a property with this key.
    """
    export_def = {
        "param": JSON_INHERITED("pkeys"),
        "key": JSON_ATTR(solo=True)
    }
    export_lookup = { "url": "url" }
    param = models.ForeignKey(Parametisation, related_name="pkeys", help_text="The Parametisation")
    key = models.CharField(max_length=120, help_text="The parametised key")
    def __unicode__(self):
        return "%s[%s]" % (self.param.name, self.key)
    class Meta:
        unique_together=[("param", "key"),]
        ordering=("param", "key")

class ParametisationValue(models.Model):
    """
    A ParametisationValue defines a virtual instance of each widget parametised by a given Parametisation.

    It encapsulates a set of values of for a :model:`Parametisation`'s keys.

    ParametisationValues are maintained automatically by signals, they should never need to be 
    manually created, deleted or modified.
    """
    param = models.ForeignKey(Parametisation, help_text="The Parametisation")
    views = models.ManyToManyField(WidgetView, help_text="The set of views whose properties match this ParametisationValue")
    def parameters(self):
        """Returns the values for the parametised keys that this object encapsulates as an associative array."""
        return { pkv.key: pkv.value() for pkv in self.parametervalue_set.all() }
    def matches_parameters(self, params):
        """Tests whether a given set of parameters (as an associative array) matches that of this ParametisationValue"""
        my_params = self.parameters()
        for k in self.param.keys():
            if k not in my_params:
                return False
            v = my_params[k]
            if k not in params:
                return False
            if my_params[k] != params[k]:
                return False
        return True
    def matches(self, view):
        """Tests whether a view's properties match this ParametisationValue"""
        return self.matches_parameters(view.properties())
    def __unicode__(self):
        return "%s: %s" % (unicode(self.param), ", ".join([ unicode(pv) for pv in self.parametervalue_set.all() ]))
    class Meta:
        ordering=("param", "id")

class ParameterValue(models.Model):
    """
    Holds a single parameter value as part of a :model:`ParametisationValue`
    """
    INT_PROPERTY=ViewProperty.INT_PROPERTY
    STR_PROPERTY=ViewProperty.STR_PROPERTY
    BOOL_PROPERTY=ViewProperty.BOOL_PROPERTY
    DEC_PROPERTY=ViewProperty.DEC_PROPERTY
    property_types=ViewProperty.property_types
    pv = models.ForeignKey(ParametisationValue)
    key = models.CharField(max_length=120)
    property_type=models.SmallIntegerField(choices=property_types.items())
    strval=models.CharField(max_length=255, blank=True, null=True)
    intval=models.IntegerField(blank=True, null=True)
    boolval=models.NullBooleanField()
    decval=models.DecimalField(decimal_places=4, max_digits=14, blank=True, null=True)
    def __unicode__(self):
        return "%s = %s" % (self.key, unicode(self.value()))
    def value(self):
        if self.property_type == self.INT_PROPERTY:
            return self.intval
        elif self.property_type == self.DEC_PROPERTY:
            return self.decval
        elif self.property_type == self.BOOL_PROPERTY:
            return self.boolval
        else:
            return self.strval
    class Meta:
        unique_together=[("pv", "key"),]
        ordering=("pv", "key")


