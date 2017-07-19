#   Copyright 2015,2016,2017 CSIRO
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
from widget_def.parametisation import parametise_label, resolve_pval
from widget_def.model_json_tools import *

# Create your models here.

tz = pytz.timezone(settings.TIME_ZONE)

def stat_unit_exporter(stat):
    members = [ "prefix", "suffix", "underfix", "signed" ]
    exp={}
    for m in members:
        mv = getattr(stat, "unit_" + m)
        if mv:
            exp[m] = mv
    return exp

class Statistic(models.Model, WidgetDefJsonMixin):
    """
    Represents a single chunk of data to be displayed in a widget. May be a scalar or a list.

    Supported statistic types include:

    Non-display-list Statistics
    ---------------------------
    string: A (short) string value.
    long_string: A long string value
    numeric: A number.   
    am_pm: An am/pm indicator.
    null: No base data - useful for eye-candy (e.g. an icon or a traffic light code) with no associated data.

    Display list statistics
    -----------------------
    string_kv_list: A list of key value pairs where the key and value are both strings.
    numeric_kv_list: A list of key value pairs where the key is a string and the value is numeric. 
        Statistics of this type should also define a unit and a precision, which apply to all values in the list.
    string_list: A list of strings.
    long_string_list: A list of long strings
    event_list: A list of key value pairs where the key is a date an the value is a string. Can only appear in a calendar type tile.
    hierarchical_event_list: A list of key value pairs where the key consists of a datetime and a "level" 
        (i.e. second, minute, hour,day, month,quarter,year); and the value is a string. 
        Can only appear in a time_line type tile.  The datetime value of each list item is rounded to the associated level.
    """
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
    NULL_STAT = 11
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list", 
                   "am_pm" , "event_list" , "long_string", "long_string_list", "hierarchical_event_list", 
                   "null" ]
    export_def = {
        "tile": JSON_INHERITED("statistics"),
        "name": JSON_ATTR(),
        "url": JSON_ATTR(),
        "name_as_label": JSON_ATTR(),
        "stat_type": JSON_ATTR(),
        "traffic_light_scale": JSON_CAT_LOOKUP(["traffic_light_scale", "name"], lambda js, k, kw: TrafficLightScale.objects.get(name=js["traffic_light_scale"])),
        "traffic_light_automation": JSON_CAT_LOOKUP(["traffic_light_automation", "url"], lambda js, k, kw: TrafficLightAutomation.objects.get(url=js["traffic_light_automation"])),
        "icon_library": JSON_CAT_LOOKUP(["icon_library", "name"], lambda js, k, kw: IconLibrary.objects.get(name=js["icon_library"])),
        "trend": JSON_ATTR(),
        "hyperlinkable": JSON_ATTR(),
        "numbered_list": JSON_ATTR(),
        "footer": JSON_ATTR(),
        "rotates": JSON_ATTR(),
        "editable": JSON_ATTR(),
        "num_precision": JSON_ATTR(),
        "unit_prefix": JSON_ATTR(),
        "unit_suffix": JSON_ATTR(),
        "unit_underfix": JSON_ATTR(),
        "unit_si_prefix_rounding": JSON_ATTR(),
        "unit_signed": JSON_ATTR(),
        "sort_order": JSON_IMPLIED(),
    }
    export_lookup = { "tile": "tile", "url": "url" }
    api_state_def = {
        "label": JSON_ATTR(attribute="url"),
        "type": JSON_EXP_ARRAY_LOOKUP(lookup_array=stat_types, attribute="stat_type"),
        "name": JSON_OPT_ATTR(decider=["tile", "is_grid"],parametise=True),
        "display_name": JSON_OPT_ATTR(decider=["tile", "is_grid"], attribute="name_as_label"),
        "precision": JSON_OPT_ATTR(decider="is_numeric", attribute="num_precision"),
        "unit": JSON_OPT_ATTR(decider="is_numeric", attribute="self", exporter=stat_unit_exporter),
        "traffic_light_scale": JSON_CONDITIONAL_EXPORT(
                lambda obj, kwargs : (obj.traffic_light_automation is None),
                JSON_PASSDOWN(),
                JSON_PASSDOWN(attribute="traffic_light_automation")
        ),
        "trend": JSON_ATTR(),
        "icon_library": JSON_CAT_LOOKUP(["icon_library", "name"], None),
        "rotates": JSON_OPT_ATTR(),
        "numbered_list": JSON_OPT_ATTR(decider="is_display_list"),
        "hyperlinkable": JSON_OPT_ATTR(decider="is_data_list"),
        "footer": JSON_ATTR()
    }
    tile = models.ForeignKey(TileDefinition, related_name="statistics", help_text="The widget tile this statistic appears in")
    name = models.CharField(max_length=80, blank=True, help_text="A pretty descriptive name for the statistic - may be blank if the statistic is be unlabeled")
    url = models.SlugField(verbose_name="A short symbolic name that identifies the statistic, used within the API")
    name_as_label=models.BooleanField(verbose_name="display_name", default=True, help_text="If true, the name field is used as the display name for the statistic. If false, a display name for the statistic is supplied dynamically with the widget data.")
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
                    (NULL_STAT, stat_types[NULL_STAT]),
                ), help_text="The statistic type")
    traffic_light_scale = models.ForeignKey(TrafficLightScale, blank=True, null=True, help_text="The traffic light scale associated with the statistic. If set, a traffic light value from the configured scale will be supplied for the statistic with the widget data. The traffic light value must be set explicitly by the data loader or uploader. (Note traffic_light_scale and traffic_light_automation cannot both be set for a statistic.)")
    traffic_light_automation = models.ForeignKey(TrafficLightAutomation, blank=True, null=True, help_text="The traffic light automation associated with the statistic. If set, a traffic light value from the configured scale will be supplied for the statistic with the widget data. The traffic light value is determined automatically from the statistic value - traffic light automation can therefore not be set for 'null' statistics. (Note traffic_light_scale and traffic_light_automation cannot both be set for a statistic.)")
    icon_library = models.ForeignKey(IconLibrary, blank=True, null=True, help_text="The icon library associated with the statistic. If set, an icon from the configured library will be supplied for the statistic with the widget data. The icon must be set explicitly by the data loader or uploader.")
    trend = models.BooleanField(default=False, help_text="If true, the statistic is be displayed with a trend arrow that can indicate 'trending upwards', 'trending downwards', or 'holding steady'. The value of the trend arrow for the statistic is supplied with the widget data.")
    rotates = models.BooleanField(default=False, help_text="For display list statistics, rotates=True means that only as many list items as can be displayed at once should be displayed, but the items displayed should be gradually rotated through the full set of list items supplied. For non-display-list statistics, rotates=True means that a list of data items will be supplied (instead of single data-item), but only one will be displayed at a time. The displayed item should gradually rotate through the full set supplied.")
    num_precision = models.SmallIntegerField(blank=True, null=True, help_text="The number of decimal places per data item. For numeric and numeric_kv_list statistics.")
    unit_prefix = models.CharField(max_length=10, blank=True, null=True, help_text="A prefix for the statistic.  e.g. '$': display 15 as '$15'.")
    unit_suffix = models.CharField(max_length=40, blank=True, null=True, help_text="A suffix for the statistic.  e.g. 'km': display 55 as '55km'.")
    unit_underfix = models.CharField(max_length=40, blank=True, null=True, help_text="A string to print under the statistic (as opposed to before or after).")
    unit_signed = models.BooleanField(default=False, help_text="For numeric and numeric_kv_list statistics only. If true, the data item is ALWAYS displayed with a sign (+ or -). If false only negative numbers are displayed with an explicit sign.")
    unit_si_prefix_rounding = models.IntegerField(default=0, help_text="""For numeric and numeric_kv_list statistics only. 
            If specified, the data item (with precision as specified) should be rounded by the front-end to the indicated number of significant digits, 
            and an SI unit prefix will be displayed between the number and any defined unit suffix. 

                Eg 1. Precision=0, si_prefix_rounding=2
                1 -> 1,    234 -> 230,   5328 -> 5.3k,   45236457 -> 45M

                Eg 2. Precision=2, si_prefix_rounding=4
                0.03 -> 30m, 12.34 -> 12.34, 234.77 -> 234.8, 2345156.43 -> 23.45M""")
    sort_order = models.IntegerField(help_text="How the statistic is sorted within the tile.")
    hyperlinkable = models.BooleanField(default=False, help_text="For display-list statistics and statistics with rotates=True. If true, an external URL can be optionally supplied for each list item.")
    footer = models.BooleanField(default=False, help_text='If true, the statistic is to be displayed as a "footer" across the bottom of the tile. Cannot be true for display list statistics, and can only be true for at most one statistic per tile.')
    editable = models.BooleanField(default=True, help_text="If true, users with the widget's 'edit_permission' can manually edit the data for this statistic. If false, only users with the widget's 'edit_all_permission' can do so.")
    numbered_list = models.BooleanField(default=False, help_text="For display-list statistics only. If true, list items should be displayed numbered.")
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
    def widget(self):
        return self.tile.widget
    def is_numeric(self):
        """Returns true if this is a numeric statistic (numeric or numeric_kv_list type)"""
        return self.stat_type in (self.NUMERIC, self.NUMERIC_KVL)
    def is_display_list(self):
        """Returns true if this a display-list statistic"""
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL,
                                self.STRING_LIST, self.LONG_STRING_LIST,
                                self.EVENT_LIST, self.HIERARCHICAL_EVENT_LIST)
    def is_data_list(self):
        """Returns true if this a display-list statistic or if self.rotates is true"""
        return self.is_display_list() or self.rotates
    def is_eventlist(self):
        """Returns true if this statistic is of type event_list or hierarchical_event_list"""
        return self.stat_type in (self.EVENT_LIST, self.HIERARCHICAL_EVENT_LIST)
    def use_datekey(self):
        """Returns true for statistics where the key of the kv list is of date type.  (event_list statistics)"""
        return self.stat_type == self.EVENT_LIST
    def use_datetimekey(self):
        """Returns true for statistics where the key of the kv list is of datetime type.  (hierarchical_event_list statistics)"""
        return self.stat_type == self.HIERARCHICAL_EVENT_LIST
    def use_datetimekey_level(self):
        """Returns true for statistics where a datetime key level is used.  (hierarchical_event_list statistics)"""
        return self.stat_type == self.HIERARCHICAL_EVENT_LIST
    def is_kvlist(self):
        """Returns true for statistics with a simple key-value list.  (string_kv_list and numeric_kv_list)"""
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL)
    def initial_form_datum(self, sd):
        """Package up the values in a :model:`widget_data.StatisticData` or :model:`widget_data.StatisticListItem` object ready for passing to a dynamic statistic form."""
        result = {}
        if self.stat_type != self.NULL_STAT:
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
        """
        Return the data for this widget (with parametisation if necessary).

        Data returned as a single :model:`widget_data.StatisticData` object or a :model:`widget_data.StatisticListItem` query result if is_data_list() returns True.
        """
        pval=resolve_pval(self.widget().parametisation,view=view,pval=pval)
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
        """
        Return the data for this widget (with parametisation if neccessary) in json format.
        """
        data = self.get_data(view, pval)
        if self.is_data_list():
            return [ self.jsonise(datum) for datum in data ]
        else:
            return self.jsonise(data)
    def jsonise(self, datum):
        """
        Converts a :model:`widget_data.StatisticData` or :model:`widget_data.StatisticListItem` datum for this statistic into json format.
        """
        json = {}
        if datum:
            if self.stat_type != self.NULL_STAT:
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
        """Package up the current data for this statistic ready for passing to a dynamic statistic form."""
        if self.is_data_list():
            return [ self.initial_form_datum(sd) for sd in self.get_data(pval=pval) ]
        else:
            sd = self.get_data(pval=pval)
            if sd:
                return self.initial_form_datum(sd)
            else:
                return {}
    def data_last_updated(self, update=False, view=None, pval=None):
        """
        Return when the data for this statistic was last updated (with parametisation if necessary).

        update: If true and the last_updated value is cached, then the cached value is dropped and recalculated.
        """
        pval=resolve_pval(self.widget().parametisation,view=view,pval=pval)
        if pval:
            if self._lud_cache and self._lud_cache.get(pval.id) and not update:
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
        return state
    class Meta:
        unique_together = [("tile", "url")]
        ordering = [ "tile", "sort_order" ]

