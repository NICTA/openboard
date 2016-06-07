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

from decimal import Decimal
import pytz

from django.conf import settings
from django.db import models

from widget_data.models import StatisticData, StatisticListItem
from widget_def.models.tile_def import TileDefinition
from widget_def.models.eyecandy import IconLibrary, TrafficLightScale, TrafficLightAutoStrategy, TrafficLightAutomation
from widget_def.parametisation import parametise_label

# Create your models here.

tz = pytz.timezone(settings.TIME_ZONE)

class Statistic(models.Model):
    _lud_cache = None
    STRING = 1
    NUMERIC = 2
    STRING_KVL = 3
    NUMERIC_KVL = 4
    STRING_LIST = 5
    AM_PM = 6
    EVENT_LIST = 7
    LONG_STRING = 8
    LONG_STRING_LIST = 9
    HIERARCHICAL_EVENT_LIST = 10
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list", 
                    "am_pm" , "event_list" , "long_string", "long_string_list", "hierarchical_event_list" ]
    tile = models.ForeignKey(TileDefinition)
    name = models.CharField(max_length=80, blank=True)
    url = models.SlugField(verbose_name="label")
    name_as_label=models.BooleanField(verbose_name="display_name", default=True)
    stat_type = models.SmallIntegerField(choices=(
                    (STRING, stat_types[STRING]),
                    (LONG_STRING, stat_types[LONG_STRING]),
                    (NUMERIC, stat_types[NUMERIC]),
                    (STRING_KVL, stat_types[STRING_KVL]),
                    (NUMERIC_KVL, stat_types[NUMERIC_KVL]),
                    (STRING_LIST, stat_types[STRING_LIST]),
                    (LONG_STRING_LIST, stat_types[LONG_STRING_LIST]),
                    (AM_PM, stat_types[AM_PM]),
                    (EVENT_LIST, stat_types[EVENT_LIST]),
                    (HIERARCHICAL_EVENT_LIST, stat_types[HIERARCHICAL_EVENT_LIST]),
                ))
    traffic_light_scale = models.ForeignKey(TrafficLightScale, blank=True, null=True)
    traffic_light_automation = models.ForeignKey(TrafficLightAutomation, blank=True, null=True)
    icon_library = models.ForeignKey(IconLibrary, blank=True, null=True)
    trend = models.BooleanField(default=False)
    rotates = models.BooleanField(default=False)
    num_precision = models.SmallIntegerField(blank=True, null=True)
    unit_prefix = models.CharField(max_length=10, blank=True, null=True)
    unit_suffix = models.CharField(max_length=40, blank=True, null=True)
    unit_underfix = models.CharField(max_length=40, blank=True, null=True)
    unit_signed = models.BooleanField(default=False)
    unit_si_prefix_rounding = models.IntegerField(default=0)
    sort_order = models.IntegerField()
    hyperlinkable = models.BooleanField(default=False)
    footer = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)
    numbered_list = models.BooleanField(default=False)
    def clean(self):
        if not self.is_numeric():
            self.num_precision = None
            self.unit_prefix = None
            self.unit_suffix = None
            self.unit_underfix = None
            self.unit_signed = False
            self.unit_si_prefix_rounding = 0
        if self.stat_type == self.AM_PM:
            self.traffic_light_scale = None
            self.icon_library = None
        if self.stat_type in (self.EVENT_LIST, self.HIERARCHICAL_EVENT_LIST):
            self.traffic_light_scale = None
            self.traffic_light_automation = None
            self.trend = False
        if self.traffic_light_automation:
            self.traffic_light_scale = None
        if self.is_display_list():
            name_as_label=True
        else:
            numbered_list=False
        if not self.is_data_list():
            self.hyperlinkable = False
    def validate(self):
        """Validate Statistic Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        self.clean()
        self.save()
        problems = []
        if self.is_numeric():
            if self.num_precision is None:
                problems.append("Statistic %s of Widget %s is numeric, but has no precision set" % (self.url, self.tile.widget.url()))
            elif self.num_precision < 0:
                problems.append("Statistic %s of Widget %s has negative precision" % (self.url, self.tile.widget.url()))
            if self.unit_si_prefix_rounding < 0:
                problems.append("Statistic %s of Widget %s has negative si_prefix_rounding" % (self.url, self.tile.widget.url()))
        if self.is_eventlist() and self.tile.tile_type not in (self.tile.TIME_LINE, self.tile.CALENDAR, self.tile.SINGLE_LIST_STAT):
            problems.append("Event List statistic only allowed on a Time Line, Calendar or Single List Statistic tile")
        if self.traffic_light_automation:
            if self.is_numeric():
                if self.traffic_light_automation.strategy.strategy_type == self.traffic_light_automation.strategy.MAP:
                    problems.append("Numeric statistics cannot use a MAP type traffic light strategy")
            else:
                if self.traffic_light_automation.strategy.strategy_type != self.traffic_light_automation.strategy.MAP:
                    problems.append("Non-Numeric statistics must use a MAP type traffic light strategy")
            problems.extend(self.traffic_light_automation.validate())
        return problems
    def __unicode__(self):
        return "%s[%s]" % (self.tile,self.name)
    def is_numeric(self):
        return self.stat_type in (self.NUMERIC, self.NUMERIC_KVL)
    def is_display_list(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL,
                                self.STRING_LIST, self.LONG_STRING_LIST,
                                self.EVENT_LIST, self.HIERARCHICAL_EVENT_LIST)
    def is_data_list(self):
        return self.is_display_list() or self.rotates
    def is_eventlist(self):
        return self.stat_type in (self.EVENT_LIST, self.HIERARCHICAL_EVENT_LIST)
    def use_datekey(self):
        return self.stat_type == self.EVENT_LIST
    def use_datetimekey(self):
        return self.stat_type == self.HIERARCHICAL_EVENT_LIST
    def use_datetimekey_level(self):
        return self.stat_type == self.HIERARCHICAL_EVENT_LIST
    def is_kvlist(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL)
    def initial_form_datum(self, sd):
        result = {}
        result["value"] = sd.value()
        if self.traffic_light_scale:
            result["traffic_light_code"] = sd.traffic_light_code.value
        if self.icon_library:
            result["icon_code"] = sd.icon_code.value
        if self.trend:
            result["trend"] = unicode(sd.trend)
        if self.hyperlinkable:
            result["url"] = sd.url
        if self.is_data_list():
            if self.is_kvlist() or not self.name_as_label:
                result["label"] = sd.keyval
            elif self.use_datekey():
                result["date"] = sd.datetime_key.astimezone(tz).date()
            elif self.use_datetimekey():
                result["datetime"] = sd.datetime_key
                if self.use_datetimekey_level():
                    result["level"] = sd.datetime_keylevel
            result["sort_order"] = sd.sort_order
        elif not self.name_as_label:
            result["label"] = sd.label
        return result
    def get_data(self, view=None, pval=None):
        if self.tile.widget.parametisation:
            if view: 
                pval = view.parametervalue_set.objects.get(param=self.tile.widget.parametisation)
        else:
            pval = None
        if self.is_data_list():
            data = StatisticListItem.objects.filter(statistic=self)
            if pval:
                return data.filter(param_value=pval)
            else:
                return data.filter(param_value__isnull=True)
        else:
            try:
                if pval:
                    return StatisticData.objects.get(statistic=self, param_value=pval)
                else:
                    return StatisticData.objects.get(statistic=self, param_value__isnull=True)
            except StatisticData.DoesNotExist:
                return None
    def get_data_json(self, view=None, pval=None):
        data = self.get_data(view, pval)
        if self.is_data_list():
            return [ self.jsonise(datum) for datum in data ]
        else:
            return self.jsonise(data)
    def jsonise(self, datum):
        json = {}
        if datum:
            json["value"] = datum.value()
            if self.is_kvlist():
                json["label"]=datum.keyval
            elif self.use_datekey():
                json["date"]=datum.display_datetime_key()
            elif self.use_datetimekey():
                json["datetime"]=datum.display_datetime_key()
                if self.use_datetimekey_level():
                    json["datetime_level"] = datum.levels[datum.datetime_keylevel]
            elif not self.name_as_label:
                if self.rotates:
                    json["label"]=datum.keyval
                else:
                    json["label"]=datum.label
            if self.hyperlinkable:
                json["url"]=datum.url
            if self.traffic_light_scale or self.traffic_light_automation:
                json["traffic_light"]=datum.traffic_light_code.value
            if self.icon_library:
                json["icon"]=datum.icon_code.__getstate__()
            if self.trend:
                json["trend"]=datum.trend
        return json
    def initial_form_data(self, pval=None):
        if self.is_data_list():
            return [ self.initial_form_datum(sd) for sd in self.get_data(pval=pval) ]
        else:
            sd = self.get_data(pval=pval)
            if sd:
                return self.initial_form_datum(sd)
            else:
                return {}
    def data_last_updated(self, update=False, view=None, pval=None):
        if self.tile.widget.parametisation:
            if view: 
                pval = view.parametervalue_set.objects.get(param=self.tile.widget.parametisation)
            if self._lud_cache and self._lud_cache[pval.id] and not update:
                return self._lud_cache[pval.id]
            if not self._lud_cache:
                self._lud_cache = {}
            if self.is_data_list():
                self._lud_cache[pval.id] = StatisticListItem.objects.filter(statistic=self,param_value=pval).aggregate(lud=models.Max('last_updated'))['lud']
            else:
                try:
                    self._lud_cache[pval.id] = StatisticData.objects.get(statistic=self,param_value=pval).last_updated
                except StatisticData.DoesNotExist:
                    self._lud_cache[pval.id] = None
            return self._lud_cache[pval.id]
        else:
            if self._lud_cache and not update:
                return self._lud_cache
            if self.is_data_list():
                self._lud_cache = StatisticListItem.objects.filter(statistic=self).aggregate(lud=models.Max('last_updated'))['lud']
            else:
                try:
                    self._lud_cache = StatisticData.objects.get(statistic=self).last_updated
                except StatisticData.DoesNotExist:
                    self._lud_cache = None
            return self._lud_cache
    def export(self):
        if self.traffic_light_scale:
            traffic_light_scale_name = self.traffic_light_scale.name
        else:
            traffic_light_scale_name = None
        if self.icon_library:
            icon_library_name = self.icon_library.name
        else:
            icon_library_name = None
        if self.traffic_light_automation:
            automation = self.traffic_light_automation.url
        else:
            automation = None
        return {
            "name": self.name,
            "url": self.url,
            "name_as_label": self.name_as_label,
            "stat_type": self.stat_type,
            "traffic_light_scale": traffic_light_scale_name,
            "traffic_light_automation": automation,
            "icon_library": icon_library_name,
            "trend": self.trend,
            "hyperlinkable": self.hyperlinkable,
            "numbered_list": self.numbered_list,
            "footer": self.footer,
            "rotates": self.rotates,
            "editable": self.editable,
            "num_precision": self.num_precision,
            "unit_prefix": self.unit_prefix,
            "unit_suffix": self.unit_suffix,
            "unit_underfix": self.unit_underfix,
            "unit_si_prefix_rounding": self.unit_si_prefix_rounding,
            "unit_signed": self.unit_signed,
            "sort_order": self.sort_order,
        }
    @classmethod
    def import_data(cls, tile, data):
        try:
            s = Statistic.objects.get(tile=tile, url=data["url"])
        except Statistic.DoesNotExist:
            s = Statistic(tile=tile, url=data["url"])
        s.name = data["name"]
        s.name_as_label = data["name_as_label"]
        s.stat_type = data["stat_type"]
        s.hyperlinkable = data.get("hyperlinkable", False)
        s.numbered_list = data.get("numbered_list", False)
        s.footer = data.get("footer", False)
        s.rotates = data.get("rotates", False)
        s.editable = data.get("editable", True)
        s.trend = data["trend"]
        s.num_precision = data["num_precision"]
        s.unit_prefix = data["unit_prefix"]
        s.unit_suffix = data["unit_suffix"]
        s.unit_underfix = data["unit_underfix"]
        s.unit_signed = data["unit_signed"]
        s.unit_si_prefix_rounding = data.get("unit_si_prefix_rounding", 0)
        s.sort_order = data["sort_order"]
        if data["traffic_light_scale"]:
            s.traffic_light_scale = TrafficLightScale.objects.get(name=data["traffic_light_scale"])
        else:
            s.traffic_light_scale = None
        if data["icon_library"]:
            s.icon_library = IconLibrary.objects.get(name=data["icon_library"])
        else:
            s.icon_library = None
        if data.get("traffic_light_automation"):
            s.traffic_light_automation = TrafficLightAutomation.objects.get(url=data["traffic_light_automation"])
        s.save()
        return s
    def __getstate__(self, view):
        state = {
            "label": self.url,
            "type": self.stat_types[self.stat_type],
        }
        if self.tile.tile_type != TileDefinition.GRID:
            state["name"] = parametise_label(self.tile.widget, view, self.name)
            state["display_name"] = self.name_as_label
        if self.is_numeric():
            state["precision"] = self.num_precision
            state["unit"] = {}
            if self.unit_prefix:
                state["unit"]["prefix"] = self.unit_prefix 
            if self.unit_suffix:
                state["unit"]["suffix"] = self.unit_suffix 
            if self.unit_underfix:
                state["unit"]["underfix"] = self.unit_underfix 
            if self.unit_signed:
                state["unit"]["signed"] = True
            if self.unit_si_prefix_rounding > 0:
                state["unit"]["si_prefix_rounding"] = self.unit_si_prefix_rounding
        if self.traffic_light_scale:
            state["traffic_light_scale"] = self.traffic_light_scale.__getstate__()
        elif self.traffic_light_automation:
            state["traffic_light_scale"] = self.traffic_light_automation.strategy.scale.__getstate__()
        else:
            state["traffic_light_scale"] = None
        if self.stat_type not in (self.STRING_LIST, self.LONG_STRING_LIST):
            state["trend"] = self.trend
            if self.icon_library:
                state["icon_library"] = self.icon_library.name
            else:
                state["icon_library"] = None
        if self.rotates:
            state["rotates"] = self.rotates
        if self.is_display_list():
            state["numbered_list"] = self.numbered_list
        if self.is_data_list():
            state["hyperlinkable"] = self.hyperlinkable
        state["footer"] = self.footer
        return state
    class Meta:
        unique_together = [("tile", "name"), ("tile", "url")]
        ordering = [ "tile", "sort_order" ]

