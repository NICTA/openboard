#   Copyright 2015, 2016, 2017 CSIRO
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
from widget_def.model_json_tools import *

# Create your models here.

class IconLibrary(models.Model, WidgetDefJsonMixin):
    """
    An icon library is collection of concepts to represented by images.

    Icons are only stored in Openboard by name. It is up to the front end implementation to
    supply the actual images.
    """
    export_def = {
        "library_name": JSON_ATTR(attribute="name"),
        "codes": JSON_RECURSEDOWN("IconCode", "codes", "scale",  "value", app="widget_def")
    }
    export_lookup = { "library_name": "name" }
    api_state_def = {
        None:  JSON_RECURSEDOWN("IconCode", "codes", "scale", "value", app="widget_def")
    }
    name=models.SlugField(unique=True, help_text="Name of the IconLibrary")
    def __unicode__(self):
        return self.name
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.codes.all() ])
        return choices

class IconCode(models.Model, WidgetDefJsonMixin):
    """
    Represents a single icon within an icon library.
    """
    export_def = {
        "scale": JSON_INHERITED("codes"),
        "sort_order": JSON_IMPLIED(),
        "value": JSON_ATTR(),
        "description": JSON_ATTR()
    }
    export_lookup= { 
        "scale": "scale",
        "value": "value"
    }
    api_state_def = {
        "library": JSON_STRINGIFY_ATTR(attribute="scale"),
        "value": JSON_ATTR(),
        "alt_text": JSON_ATTR(attribute="description"),
    }
    scale=models.ForeignKey(IconLibrary, related_name="codes", verbose_name="Library", help_text="The IconLibrary this IconCode belongs to")
    value=models.SlugField(help_text="A short symbolic label for the icon, as used in the API")
    description=models.CharField(max_length=80, help_text="A longer description of the icon")
    sort_order=models.IntegerField(help_text="icons are sorted within a library by this field")
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]
 
class TrafficLightScale(models.Model, WidgetDefJsonMixin):
    """
    Represents a scale of colours used to represent the intensity or severity of a metric.
    """
    export_def = {
        "scale_name": JSON_ATTR(attribute="name"),
        "codes": JSON_RECURSEDOWN("TrafficLightScaleCode", "codes", "scale", "value", app="widget_def")
    }
    export_lookup={ "scale_name": "name" }
    api_state_def = {
        "scale": JSON_ATTR(attribute="name"),
        "codes": JSON_RECURSEDOWN("TrafficLightScaleCode", "codes", "scale", "value", app="widget_def")
    }
    name=models.CharField(max_length=80, unique=True, help_text="Identifies the traffic light scale")
    def __unicode__(self):
        return self.name
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.codes.all() ])
        return choices

class TrafficLightScaleCode(models.Model, WidgetDefJsonMixin):
    """
    Represents a colour in a :model:`TrafficLightScale`.
    """
    export_def = {
        "scale": JSON_INHERITED("codes"),
        "sort_order": JSON_IMPLIED(),
        "value": JSON_ATTR(),
        "colour": JSON_ATTR()
    }
    export_lookup= { 
        "scale": "scale",
        "value": "value"
    }
    api_state_def = {
        "value": JSON_ATTR(),
        "colour": JSON_ATTR(),
    }
    scale = models.ForeignKey(TrafficLightScale, related_name="codes", help_text="The traffic light scale")
    value = models.SlugField(help_text="A short symbolic representation of the intensity/severity this code represents, as used in the API")
    colour = models.CharField(max_length=50, help_text="A description of the actual colour.  May exactl specify the colour (e.g. a hex code) but in general the exact colour scheme should be left to the front end implementation")
    sort_order = models.IntegerField(help_text='"Good" codes should have lower sort order than "Bad" codes.')
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]

class TrafficLightAutoStrategy(models.Model, WidgetDefJsonMixin):
    """
    Describes a method by which statistic values can be automatically mapped to :model:`TrafficLightScaleCode`s.

    Supported strategy types are:

    RELATIVE: Traffic light code is determined from the ratio of a numeric statistic value to a defined target value.

    ABSOLUTE: Traffic light code is determined directly from a numeric statistic value.

    MAP: Traffic light code is mapped from a string statistic value.
    """
    export_def = {
        "url": JSON_ATTR(),
        "type": JSON_ATTR(attribute="strategy_type"),
        "scale": JSON_STRINGIFY_ATTR(),
        "rules": JSON_RECURSEDOWN("TrafficLightAutoRule", "rules", "strategy", None, merge=False, app="widget_def")
    }
    export_lookup={ "url": "url" }
    RELATIVE = 1
    ABSOLUTE = 2
    MAP = 3
    url = models.SlugField(unique=True, help_text="Identifies the automation strategy")
    strategy_types = [ "-", "relative", "absolute", "map" ]
    scale = models.ForeignKey(TrafficLightScale, help_text="The TrafficLightScale this strategy automates")
    strategy_type = models.SmallIntegerField(choices=(
                    (RELATIVE, strategy_types[RELATIVE]),
                    (ABSOLUTE, strategy_types[ABSOLUTE]),
                    (MAP, strategy_types[MAP]),
            ), help_text="""The type of automation strategy. Supported strategy types are:

            RELATIVE: Traffic light code is determined from the ratio of a numeric statistic value to a defined target value.

            ABSOLUTE: Traffic light code is determined directly from a numeric statistic value.

            MAP: Traffic light code is mapped from a string statistic value.
            """)
    def __unicode__(self):
        return self.url
    def validate(self):
        problems = []
        for r in self.rules.all():
            problems.extend(r.validate())
        try:
            d = self.rules.get(default_val=True)
        except TrafficLightAutoRule.DoesNotExist:
            problems.append("Non-map Traffic Light Auto-Strategy %s does not have a default value" % self.url)
        except TrafficLightAutoRule.MultipleObjectsReturned:
            problems.append("Traffic Light Auto-Strategy %s has multiple default values" % self.url)
        return problems
    def traffic_light_for(self, val, target_val=None):
        """
        Use this strategy to determine the traffic light code for a given statistic value.

        val: The statistic value to determine the traffic light code for.

        target_val: The target value for RELATIVE strategies.
        """
        rules = self.rules.filter(default_val=False)
        default_rule = self.rules.get(default_val=True)
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

class TrafficLightAutoRule(models.Model, WidgetDefJsonMixin):
    """
    A rule from a :model:`TrafficLightAutoStrategy`

    Consists of a traffic light code and a rule for when to use it.
    """
    export_def = {
        "map_val": JSON_ATTR(),
        "is_default": JSON_ATTR(attribute="default_val"),
        "code": JSON_CAT_LOOKUP(["code", "value"],
                lambda js, key, imp_kwargs: TrafficLightScaleCode.objects.get(scale=imp_kwargs["strategy"].scale, value=js["code"])),
        "min_val": JSON_NUM_ATTR(4)
    }
    strategy=models.ForeignKey(TrafficLightAutoStrategy, related_name="rules", help_text="The automation strategy this rule is a part of")
    min_val=models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="The minimum value for which this rule applies. Required for absolute and relative strategies (unless default_val is set).")
    map_val=models.CharField(max_length=400, null=True, blank=True, help_text="The string value for which this rule applies. Required for map strategies (unless default_val is set)")
    default_val=models.BooleanField(default=False, help_text="If true, then this is the default rule which applies if no other rule matches. There should be one and only one default value rule per automation strategy.")
    code = models.ForeignKey(TrafficLightScaleCode, help_text="The traffic light code to use if this rule applies.")
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

class TrafficLightAutomation(models.Model, WidgetDefJsonMixin):
    """
    An actual traffic light automation instance.

    Consists of a :model:`TrafficLightAutoStrategy` and a statistic to be automated.  
    (And also a target value if the strategy is of RELATIVE type.)
    """
    export_def = {
        "url": JSON_ATTR(),
        "strategy": JSON_STRINGIFY_ATTR(),
        "target_value": JSON_NUM_ATTR(precision=4),
        "target_statistic": JSON_COMPLEX_LOOKUP_WRAPPER(
                attribute="target_statistic",
                null=True,
                exporter=lambda o: { "widget": o.tile.widget.url(), "label": o.tile.widget.label, "url": o.url },
                model="Statistic",
                app="widget_def",
                importer_kwargs=lambda js: {
                            "tile__widget__family__url": js["widget"],
                            "tile__widget__label": js["label"],
                            "url": js["url"]
                },
                warning_on_importer_fail="Warning: Incomplete import of TrafficLightAutomation %s target statistic doesn't exist. You will need to set\n\tthe target statistic or value manually, or reimport after importing the relevant widget.",
                name_key_for_warning="url"
        )
    }
    export_lookup = { "url": "url" }
    url = models.SlugField(unique=True, help_text="Identifies the automation")
    # 2,4  ==>  Statistic.NUMERIC, Statistic.NUMERIC_KVL
    # Can't reference directly because of circular dependencies.  Think on this.
    target_statistic = models.ForeignKey("widget_def.Statistic", 
                        null=True, blank=True, limit_choices_to={'stat_type__in': (2,4)},
                        help_text="The statistic being automated - should be either numeric or string statistic.")
    target_value = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True, help_text="The target value (for relative automation strategies)")
    strategy = models.ForeignKey(TrafficLightAutoStrategy, help_text="The automation strategy")
    def __unicode__(self):
        return self.url
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

