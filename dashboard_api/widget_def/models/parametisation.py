#   Copyright 2016 NICTA
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
from widget_def.models.views import WidgetView, ViewProperty

# Create your models here.

class ViewDoesNotHaveAllKeys(Exception):
    pass

class Parametisation(models.Model):
    url=models.SlugField(unique=True)
    name=models.CharField(max_length=128, unique=True)
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)
    def export(self):
        return {
            "url": self.url,
            "name": self.name,
            "keys": self.keys(),
        }
    def add_key(self, key):
        return ParametisationKey.objects.get_or_create(param=self, key=key)[0]
    def delete_key(self, key):
        try:
            ParametisationKey.objects.get(param=self, key=key).delete()
        except ParametisationKey.DoesNotExist:
            pass
    def keys(self):
        return [ pk.key for pk in self.parametisationkey_set.all() ]
    def update(self, view=None):
        if not view:
            for v in WidgetView.objects.all():
                self.update(v)
            for pv in self.parametisationvalue_set.all():
                if pv.views.count() == 0:
                    pv.delete()
            return
        keys = self.keys()
        if view.viewproperty_set.filter(key__in=keys).count() < len(keys):
            pvs = list(view.parametisationvalue_set.all())
            view.parametisationvalue_set.clear()
            for pv in pvs:
                if pv.views.count() == 0:
                    pv.delete()
            return
        try:
            pv = view.parametisationvalue_set.get(param=self)
        except ParametisationValue.DoesNotExist:
            for pv in self.parametisationvalue_set.all():
                if pv.matches(view):
                    pv.views.add(view)
                    return
            pv = ParametisationValue(param=self)
            pv.save()

        pv_params = pv.parameters()
        v_params  = view.properties()
        for key in keys:
            if key not in v_params:
                pv.views.remove(view)
                if pv.views.count() == 0:
                    pv.delete()
                return
            if key not in pv_params:
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
                pv.views.remove(view)
                if pv.views.count() == 0:
                    pv.delete()
                return
        pv = ParametisationValue(param=self)
        pv.save()
        for prop in view.viewproperty_set.filter(key__in=keys):
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
    @classmethod
    def update_all(cls, view=None):
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

class ParametisationKey(models.Model):
    param = models.ForeignKey(Parametisation)
    key = models.CharField(max_length=120)
    def __unicode__(self):
        return "%s[%s]" % (self.param.name, self.key)
    class Meta:
        unique_together=[("param", "key"),]
        ordering=("param", "key")

class ParametisationValue(models.Model):
    param = models.ForeignKey(Parametisation)
    views = models.ManyToManyField(WidgetView)
    def parameters(self):
        return { pkv.key: pkv.value() for pkv in self.parametervalue_set.all() }
    def matches_parameters(self, params):
        my_params = self.parameters()
        for k in params:
            if k not in my_params:
                return False
            v = my_params[k]
            if k not in params:
                return False
            if my_params[k] != params[k]:
                return False
        return True
    def matches(self, view):
        return self.matches_parameters(view.properties())
    def __unicode__(self):
        return "%s: %s" % (unicode(self.param), ", ".join([ unicode(pv) for pv in self.parametervalue_set.all() ]))
    
class ParameterValue(models.Model):
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


