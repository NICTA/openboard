#   Copyright 2015, 2016 NICTA
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
from django.apps import apps
from django.db import models

# Create your models here.

class IconLibrary(models.Model):
    name=models.SlugField(unique=True)
    def __unicode__(self):
        return self.name
    def __getstate__(self):
        return [ c.__getstate__() for c in self.iconcode_set.all() ]
    def export(self):
        return {
            "library_name": self.name,
            "codes": [ c.export() for c in self.iconcode_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            l = IconLibrary.objects.get(name=data["library_name"])
        except IconLibrary.DoesNotExist:
            l = IconLibrary(name=data["library_name"])
            l.save()
        values = []
        for c in data["codes"]:
            IconCode.import_data(l, c)
            values.append(c["value"])
        for code in l.iconcode_set.all():
            if code.value not in values:
                code.delete()
        return l
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.iconcode_set.all() ])
        return choices

class IconCode(models.Model):
    scale=models.ForeignKey(IconLibrary)
    value=models.SlugField()
    description=models.CharField(max_length=80)
    sort_order=models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    def export(self):
        return {
            "value": self.value,
            "description": self.description,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, library, data):
        try:
            code = IconCode.objects.get(scale=library, value=data["value"])
        except IconCode.DoesNotExist:
            code = IconCode(scale=library, value=data["value"])
        code.description = data["description"]
        code.sort_order = data["sort_order"]
        code.save()
        return code
    def __getstate__(self):
        return {
            "library": self.scale.name,
            "value": self.value,
            "alt_text": self.description
        }
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]
 
class TrafficLightScale(models.Model):
    name=models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name
    def export(self):
        return {
            "scale_name": self.name,
            "codes": [ c.export() for c in self.trafficlightscalecode_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            l = TrafficLightScale.objects.get(name=data["scale_name"])
        except TrafficLightScale.DoesNotExist:
            l = TrafficLightScale(name=data["scale_name"])
            l.save()
        values = []
        for c in data["codes"]:
            TrafficLightScaleCode.import_data(l, c)
            values.append(c["value"])
        for code in l.trafficlightscalecode_set.all():
            if code.value not in values:
                code.delete()
        return l
    def __getstate__(self):
        return {
            "scale": self.name,
            "codes": [ c.__getstate__() for c in self.trafficlightscalecode_set.all() ]
        }
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.trafficlightscalecode_set.all() ])
        return choices

class TrafficLightScaleCode(models.Model):
    scale = models.ForeignKey(TrafficLightScale)
    value = models.SlugField()
    colour = models.CharField(max_length=50)
    sort_order = models.IntegerField(help_text='"Good" codes should have lower sort order than "Bad" codes.')
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    def export(self):
        return {
            "value": self.value,
            "colour": self.colour,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, scale, data):
        try:
            code = TrafficLightScaleCode.objects.get(scale=scale, value=data["value"])
        except TrafficLightScaleCode.DoesNotExist:
            code = TrafficLightScaleCode(scale=scale, value=data["value"])
        code.colour = data["colour"]
        code.sort_order = data["sort_order"]
        code.save()
        return code
    def __getstate__(self):
        return {
            "value": self.value,
            "colour": self.colour
        }
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]

class TrafficLightAutoStrategy(models.Model):
    RELATIVE = 1
    ABSOLUTE = 2
    MAP = 3
    url = models.SlugField(unique=True)
    strategy_types = [ "-", "relative", "absolute", "map" ]
    scale = models.ForeignKey(TrafficLightScale)
    strategy_type = models.SmallIntegerField(choices=(
                    (RELATIVE, strategy_types[RELATIVE]),
                    (ABSOLUTE, strategy_types[ABSOLUTE]),
                    (MAP, strategy_types[MAP]),
            ))
    def rules(self):
        return self.trafficlightautorule_set
    def __unicode__(self):
        return self.url
    def export(self):
        return {
            "url": self.url,
            "type": self.strategy_type,
            "scale": self.scale.name,
            "rules": [ r.export() for r in self.rules().all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            tlas = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            tlas = cls(url=data["url"])
        tlas.strategy_type = data["type"]
        tlas.scale = TrafficLightScale.objects.get(name=data["scale"])
        tlas.save()
        tlas.rules().all().delete()
        for r in data["rules"]:
            TrafficLightAutoRule.import_data(tlas, r)
        return tlas
    def validate(self):
        problems = []
        for r in self.rules().all():
            problems.extend(r.validate())
        try:
            d = self.rules().get(default_val=True)
        except TrafficLightAutoRule.DoesNotExist:
            problems.append("Non-map Traffic Light Auto-Strategy %s does not have a default value" % self.url)
        except TrafficLightAutoRule.MultipleObjectsReturned:
            problems.append("Traffic Light Auto-Strategy %s has multiple default values" % self.url)
        return problems
    def traffic_light_for(self, val, target_val=None):
        rules = self.rules().filter(default_val=False)
        default_rule = self.rules().get(default_val=True)
        if self.strategy_type == self.RELATIVE and target_val:
            # Scale val to target_val
            val = val / target_val * decimal.Decimal("100.0")
        for rule in rules:
            if self.strategy_type == self.MAP:
                if rule.map_val == val:
                    return rule.code
            else:
                if val >= rule.min_val:
                    return rule.code
        return default_rule.code
    class Meta:
        ordering=("url",)

class TrafficLightAutoRule(models.Model):
    strategy=models.ForeignKey(TrafficLightAutoStrategy)
    min_val=models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    map_val=models.CharField(max_length=400, null=True, blank=True)
    default_val=models.BooleanField(default=False)
    code = models.ForeignKey(TrafficLightScaleCode)
    def export(self):
        data = {
            "map_val": self.map_val,
            "is_default": self.default_val,
            "code": self.code.value,
        }
        if self.min_val is None:
            data["min_val"] = None
        elif self.min_val == self.min_val.to_integral_value():
            data["min_val"] = int(self.min_val)
        else:
            data["min_val"] = float(self.min_val)
        return data
    @classmethod
    def import_data(cls, strategy, data):
        r = cls(strategy=strategy)
        r.map_val = data["map_val"]
        r.default_val = data["is_default"]
        if data["min_val"] is not None:
            r.min_val = decimal.Decimal("%.4f" % data["min_val"])
        r.code = TrafficLightScaleCode.objects.get(scale=strategy.scale, value=data["code"])
        r.save()
        return r
    def clean(self):
        if self.strategy.strategy_type == self.strategy.MAP:
            self.min_val = None
        else:
            self.map_val = None
        if self.default_val:
            self.min_val = None
            self.map_val = None
    def validate(self):
        problems = []
        try:
            self.clean()
            self.save()
            if not self.default_val:
                if self.strategy.strategy_type == self.strategy.MAP and not self.map_val:
                    problems.append("Non default rule in map strategy does not have map_val set.")
                elif self.strategy.strategy_type != self.strategy.MAP and not self.min_val:
                    problems.append("Non default rule in non-map strategy does not have min_val set.")
        except Exception, e:
            problems.append("Could not clean rule: %s" % unicode(e))
        if self.code.scale != self.strategy.scale:
            problems.append("Rule code does not belong to the strategy scale")
        return problems
    class Meta:
        unique_together=(("strategy", "default_val", "min_val", "map_val"))
        ordering=("strategy", "default_val", "-min_val", "map_val")

class TrafficLightAutomation(models.Model):
    url = models.SlugField(unique=True)
    # 2,4  ==>  Statistic.NUMERIC, Statistic.NUMERIC_KVL
    # Can't reference directly because of circular dependencies.  Think on this.
    target_statistic = models.ForeignKey("widget_def.Statistic", 
                        null=True, blank=True, limit_choices_to={'stat_type__in': (2,4)})
    target_value = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strategy = models.ForeignKey(TrafficLightAutoStrategy)
    def __unicode__(self):
        return self.url
    def export(self):
        data = {
            "url": self.url,
            "strategy": self.strategy.url
        }
        if self.target_statistic:
            data["target_statistic"] = {
                "widget": self.target_statistic.tile.widget.url(),
                "label": self.target_statistic.tile.widget.label,
                "url": self.target_statistic.url
            }
        else:
            data["target_statistic"] = None
        if self.target_value is None:
            data["target_value"] = None
        elif self.target_value == self.target_value.to_integral_value():
            data["target_value"] = int(self.target_value)
        else:
            data["target_value"] = float(self.target_value)
        return data
    @classmethod
    def import_data(cls, data):
        try:
            tla = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            tla = cls(url=data["url"])
        tla.strategy = TrafficLightAutoStrategy.objects.get(url=data["strategy"])
        if data["target_statistic"] is None:
            tla.target_statistic = None
        else:
            Statistic = apps.get_app_config("widget_def").get_model("Statistic")
            try:
                tla.target_statistic = Statistic.objects.get(tile__widget__family__url=data["target_statistic"]["widget"],
                                tile__widget__label=data["target_statistic"]["label"],
                                url=data["target_statistic"]["url"])
            except Statistic.DoesNotExist:
                tla.target_statistic = None
                tla.target_value = Decimal("100.0")
                print "Warning: Incomplete import of TrafficLightAutomation %s target statistic doesn't exist. You will need to set\n\tthe target statistic or value manually, or reimport after importing the relevant widget." % tla.url
        if data["target_value"] is None:
            tla.target_value = None
        else:
            tla.target_value = Decimal(data["target_value"])
        tla.save()
        return tla
    def validate(self):
        problems = []
        if self.target_statistic and self.target_value is not None:
            problems.append("Cannot have both target statistic and target value")
        if self.strategy.strategy_type == self.strategy.RELATIVE:
            if not (self.target_statistic or self.target_value is not None):
                problems.append("RELATIVE type strategies must set a target statistic or a target value")
        else:
            if self.target_statistic or self.target_value is not None:
                problems.append("Non-RELATIVE type strategies cannot have a target statistic or a target value")
        if self.target_statistic:
            if not self.target_statistic.is_numeric():
                problems.append("Target statistic must be a numeric statistic")
            if self.target_statistic.is_data_list():
                problems.append("Target statistic must be a scalar statistic (i.e. not a list or a rotating statistic)")
            if self.target_statistic.traffic_light_automation:
                problems.append("Target statistic cannot itself have a traffic light automation")
        return problems

