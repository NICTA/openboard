from django.db import models

from widget_data.models import StatisticData, StatisticListItem
from widget_def.models.tile_def import TileDefinition
from widget_def.models.eyecandy import IconLibrary, TrafficLightScale

# Create your models here.

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
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list", "am_pm" , "event_list" , "long_string", "long_string_list" ]
    tile = models.ForeignKey(TileDefinition)
    name = models.CharField(max_length=80, blank=True)
    url = models.SlugField()
    name_as_label=models.BooleanField(default=True)
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
                ))
    traffic_light_scale = models.ForeignKey(TrafficLightScale, blank=True, null=True)
    icon_library = models.ForeignKey(IconLibrary, blank=True, null=True)
    trend = models.BooleanField(default=False)
    rotates = models.BooleanField(default=False)
    num_precision = models.SmallIntegerField(blank=True, null=True)
    unit_prefix = models.CharField(max_length="10", blank=True, null=True)
    unit_suffix = models.CharField(max_length="10", blank=True, null=True)
    unit_underfix = models.CharField(max_length="40", blank=True, null=True)
    unit_signed = models.BooleanField(default=False)
    sort_order = models.IntegerField()
    hyperlinkable = models.BooleanField(default=False)
    footer = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)
    def clean(self):
        if not self.is_numeric():
            self.num_precision = None
            self.unit_prefix = None
            self.unit_suffix = None
            self.unit_underfix = None
            self.unit_signed = False
        if self.stat_type == self.AM_PM:
            self.traffic_light_scale = None
            self.icon_library = None
        if self.stat_type == self.EVENT_LIST:
            self.traffic_light_scale = None
            self.trend = False
        if self.is_display_list():
            name_as_label=True
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
        if self.is_eventlist() and self.tile.tile_type not in (self.tile.CALENDAR, self.tile.SINGLE_LIST_STAT):
            problems.append("Event List statistic only allowed on a Calendar or Single List Statistic tile")
        return problems
    def __unicode__(self):
        return "%s[%s]" % (self.tile,self.name)
    def is_numeric(self):
        return self.stat_type in (self.NUMERIC, self.NUMERIC_KVL)
    def is_display_list(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL,
                                self.STRING_LIST, self.LONG_STRING_LIST,
                                self.EVENT_LIST)
    def is_data_list(self):
        return self.is_display_list() or self.rotates
    def is_eventlist(self):
        return self.stat_type == (self.EVENT_LIST)
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
            elif self.is_eventlist():
                result["date"] = sd.datekey
            result["sort_order"] = sd.sort_order
        elif not self.name_as_label:
            result["label"] = sd.label
        return result
    def get_data(self):
        if self.is_data_list():
            return StatisticListItem.objects.filter(statistic=self)
        else:
            try:
                return StatisticData.objects.get(statistic=self)
            except StatisticData.DoesNotExist:
                return None
    def get_data_json(self):
        data = self.get_data()
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
            elif self.is_eventlist():
                json["date"]=datum.datekey.strftime("%Y-%m-%d")
            elif not self.name_as_label:
                if self.rotates:
                    json["label"]=datum.keyval
                else:
                    json["label"]=datum.label
            if self.hyperlinkable:
                json["url"]=datum.url
            if self.traffic_light_scale:
                json["traffic_light"]=datum.traffic_light_code.value
            if self.icon_library:
                json["icon"]=datum.icon_code.__getstate__()
            if self.trend:
                json["trend"]=datum.trend
        return json
    def initial_form_data(self):
        if self.is_data_list():
            return [ self.initial_form_datum(sd) for sd in self.get_data() ]
        else:
            sd = self.get_data()
            if sd:
                return self.initial_form_datum(sd)
            else:
                return {}
    def data_last_updated(self, update=False):
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
        return {
            "name": self.name,
            "url": self.url,
            "name_as_label": self.name_as_label,
            "stat_type": self.stat_type,
            "traffic_light_scale": traffic_light_scale_name,
            "icon_library": icon_library_name,
            "trend": self.trend,
            "hyperlinkable": self.hyperlinkable,
            "footer": self.footer,
            "rotates": self.rotates,
            "editable": self.editable,
            "num_precision": self.num_precision,
            "unit_prefix": self.unit_prefix,
            "unit_suffix": self.unit_suffix,
            "unit_underfix": self.unit_underfix,
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
        s.footer = data.get("footer", False)
        s.rotates = data.get("rotates", False)
        s.editable = data.get("editable", True)
        s.trend = data["trend"]
        s.num_precision = data["num_precision"]
        s.unit_prefix = data["unit_prefix"]
        s.unit_suffix = data["unit_suffix"]
        s.unit_underfix = data["unit_underfix"]
        s.unit_signed = data["unit_signed"]
        s.sort_order = data["sort_order"]
        if data["traffic_light_scale"]:
            s.traffic_light_scale = TrafficLightScale.objects.get(name=data["traffic_light_scale"])
        else:
            s.traffic_light_scale = None
        if data["icon_library"]:
            s.icon_library = IconLibrary.objects.get(name=data["icon_library"])
        else:
            s.icon_library = None
        s.save()
        return s
    def __getstate__(self):
        state = {
            "url": self.url,
            "type": self.stat_types[self.stat_type],
        }
        if self.tile.tile_type != TileDefinition.GRID:
            state["name"] = self.name
            state["name_as_label"] = self.name_as_label
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
        if self.traffic_light_scale:
            state["traffic_light_scale"] = self.traffic_light_scale.__getstate__()
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
        if self.is_data_list():
            state["hyperlinkable"] = self.hyperlinkable
        state["footer"] = self.footer
        return state
    class Meta:
        unique_together = [("tile", "name"), ("tile", "url")]
        ordering = [ "tile", "sort_order" ]

