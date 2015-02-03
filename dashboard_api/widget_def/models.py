from django.db import models

# Create your models here.

class Theme(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.name
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.name
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Frequency(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "frequencies"
        ordering=("sort_order",)
    def __getstate__(self):
        return {"name": self.name, "url": self.url}

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        ordering=("sort_order",)

class WidgetDefinition(models.Model):
    themes = models.ManyToManyField(Theme)
    category = models.ForeignKey(Category)
    location = models.ForeignKey(Location)
    frequency = models.ForeignKey(Frequency)
    name = models.CharField(max_length=60)
    url  = models.SlugField()
    expansion_hint = models.CharField(max_length=80)
    source_url = models.URLField(max_length=400)
    actual_frequency = models.CharField(max_length=40)
    refresh_rate = models.IntegerField()
    sort_order = models.IntegerField()
    def __getstate__(self):
        return {
            "category": self.category.name,
            "name": self.name,
            "url": self.url,
            "display": {
                "expansion_hint": self.expansion_hint,
                "tiles": [ tile.__getstate__() for tile in self.tiledefinition_set.all() ],
            },
            "source_url": self.source_url,
            "actual_frequency": self.actual_frequency,
            "refresh_rate": self.refresh_rate,
        }
    def __unicode__(self):
        return "%s (%s:%s)" % (self.name, self.location.name, self.frequency.name)
    class Meta:
        unique_together = (
            ("location", "frequency", "name"),
            ("location", "frequency", "url"),
            ("location", "frequency", "category", "sort_order"),
        )
        ordering = ("location", "frequency", "category", "sort_order")

class TileDefinition(models.Model):
    SINGLE_MAIN_STAT = 1
    DOUBLE_MAIN_STAT = 2
    PRIORITY_LIST = 3
    URGENCY_LIST = 4
    LIST_OVERFLOW = 5
    GRAPH = 6
    MAP = 7
    tile_types = [ "-", "single_main_stat", "double_main_stat", "priority_list", "urgency_list", "list_overflow", "graph", "map" ]
    widget = models.ForeignKey(WidgetDefinition)
    tile_type = models.SmallIntegerField(choices=(
                    (SINGLE_MAIN_STAT, tile_types[SINGLE_MAIN_STAT]),
                    (DOUBLE_MAIN_STAT, tile_types[DOUBLE_MAIN_STAT]),
                    (PRIORITY_LIST, tile_types[PRIORITY_LIST]),
                    (URGENCY_LIST, tile_types[URGENCY_LIST]),
                    (LIST_OVERFLOW, tile_types[LIST_OVERFLOW]),
                    (GRAPH, tile_types[GRAPH]),
                    # (MAP, tile_types[MAP]),
                ))
    expansion =  models.BooleanField(default=False)
    sort_order = models.IntegerField()
    am_pm = models.BooleanField(default=False)
    def clean(self):
        # am_pm only for single_main_stat
        if self.tile_type != self.SINGLE_MAIN_STAT:
            self.am_pm = False
    def __getstate__(self):
        state = {
            "type": self.tile_types[self.tile_type],
            "expansion": unicode(self.expansion).lower()
        }
        if self.tile_type == self.SINGLE_MAIN_STAT:
            state["am_pm"] = unicode(self.am_pm).lower()
        if self.tile_type in (self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, self.PRIORITY_LIST, self.URGENCY_LIST):
            state["statistics"] = [ s.__getstate__() for s in self.statistic_set.all() ]
        if self.tile_type == self.GRAPH:
            pass # TODO
        if self.tile_type == self.MAP:
            pass # TODO
        return state
    # graph_def, map_def
    def __unicode__(self):
        if self.expansion:
            return "%s (expansion tile %d)" % (unicode(self.widget), self.sort_order)
        else:
            return "%s (default tile)" % (unicode(self.widget))
    class Meta:
        unique_together=[("widget", "sort_order")]
        ordering=["widget", "sort_order"]

class TrafficLightScale(models.Model):
    name=models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name
    def __getstate__(self):
        return [ c.__getstate__() for c in self.trafficlightscalecode_set.all() ]

class TrafficLightScaleCode(models.Model):
    scale = models.ForeignKey(TrafficLightScale)
    value = models.SlugField()
    colour = models.CharField(max_length=50)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    def __getstate__(self):
        return {
            "value": self.value,
            "colour": self.colour
        }
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]
   
class Statistic(models.Model):
    STRING = 1
    NUMERIC = 2
    STRING_KVL = 3
    NUMERIC_KVL = 4
    STRING_LIST = 5
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list" ]
    tile = models.ForeignKey(TileDefinition)
    name = models.SlugField(blank=True)
    stat_type = models.SmallIntegerField(choices=(
                    (STRING, stat_types[STRING]),
                    (NUMERIC, stat_types[NUMERIC]),
                    (STRING_KVL, stat_types[STRING_KVL]),
                    (NUMERIC_KVL, stat_types[NUMERIC_KVL]),
                    (STRING_LIST, stat_types[STRING_LIST]),
                ))
    traffic_light_scale = models.ForeignKey(TrafficLightScale, blank=True, null=True)
    trend = models.BooleanField(default=False)
    num_precision = models.SmallIntegerField(blank=True, null=True)
    unit_prefix = models.CharField(max_length="10", blank=True, null=True)
    unit_suffix = models.CharField(max_length="10", blank=True, null=True)
    unit_underfix = models.CharField(max_length="40", blank=True, null=True)
    unit_signed = models.BooleanField(default=False)
    sort_order = models.IntegerField()
    def clean(self):
        if self.stat_type not in (self.NUMERIC, self.NUMERIC_KVL):
            self.num_precision = None
            self.unit_prefix = None
            self.unit_suffix = None
            self.unit_underfix = None
            self.unit_signed = False
        if self.stat_type == self.STRING_LIST:
            self.traffic_light_scale == None
    def __unicode__(self):
        return "%s[%s]" % (self.tile,self.name)
    def __getstate__(self):
        state = {
            "name": self.name,
            "type": self.stat_types[self.stat_type]
        }
        if self.stat_type in ( self.NUMERIC, self.NUMERIC_KVL ):
            state["precision"] = self.num_precision
            state["unit"] = {}
            if self.unit_prefix:
                state["unit"]["prefix"] = self.unit_prefix 
            if self.unit_suffix:
                state["unit"]["suffix"] = self.unit_suffix 
            if self.unit_underfix:
                state["unit"]["underfix"] = self.unit_underfix 
            if self.unit_signed:
                state["unit"]["signed"] = "true"
        if self.stat_type != self.STRING_LIST:
            state["trend"] = unicode(self.trend).lower()
            if self.traffic_light_scale:
                state["traffic_light_scale"] = self.traffic_light_scale.__getstate__()
            else:
                state["traffic_light_scale"] = None
        return state
    class Meta:
        unique_together = [("tile", "name")]
        ordering = [ "tile", "sort_order" ]

