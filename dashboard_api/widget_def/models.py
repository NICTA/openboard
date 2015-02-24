from django.db import models
from widget_data.models import StatisticData, StatisticListItem

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

class Subcategory(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=60)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.category.name, self.name)
    class Meta:
        unique_together=(('category', 'name'), ('category', 'sort_order'))
        ordering= ('category', 'sort_order')
 
class WidgetDefinition(models.Model):
    _lud_cache = None
    subcategory = models.ForeignKey(Subcategory)
    name = models.CharField(max_length=60)
    url  = models.SlugField()
    expansion_hint = models.CharField(max_length=80)
    source_url = models.URLField(max_length=400)
    actual_frequency = models.CharField(max_length=40)
    actual_frequency_url = models.SlugField()
    refresh_rate = models.IntegerField(help_text="in seconds")
    sort_order = models.IntegerField()
    about = models.TextField(null=True, blank=True)
    def validate(self):
        """Validate Widget Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        if not self.about:
            problems.append("Widget %s has no 'about' information" % self.url)
        if self.widgetdeclaration_set.all().count() == 0:
            problems.append("Widget %s has no declarations" % self.url)
        default_tiles = self.tiledefinition_set.filter(expansion=False).count()
        if default_tiles != 1:
            problems.append("Widget %s has %d default (non-expansion) tiles - must have one and only one" % (self.url, default_tiles))
        tiles = self.tiledefinition_set.all()
        stat_urls = {}
        for stat in Statistic.objects.filter(tile__widget=self):
            if stat.url in stat_urls:
                problems.append("Widget %s has two statistics with url '%s' (in tiles %s and %s)" % (self.url, stat.url, stat.tile.url, stat_urls[stat.url]))
            else:
                stat_urls[stat.url] = stat.tile.url
        for tile in tiles:
            problems.extend(tile.validate())
        return problems
    def __getstate__(self):
        return {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "name": self.name,
            "url": self.url,
            "display": {
                "expansion_hint": self.expansion_hint,
                "tiles": [ tile.__getstate__() for tile in self.tiledefinition_set.all() ],
            },
            "source_url": self.source_url,
            "actual_frequency": self.actual_frequency,
            "refresh_rate": self.refresh_rate,
            "about": self.about,
        }
    def export(self):
        return {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "name": self.name,
            "url": self.url,
            "expansion_hint": self.expansion_hint,
            "source_url": self.source_url,
            "actual_frequency": self.actual_frequency,
            "actual_frequency_url": self.actual_frequency_url,
            "refresh_rate": self.refresh_rate,
            "sort_order": self.sort_order,
            "about": self.about,
            "tiles": [ t.export() for t in self.tiledefinition_set.all() ],
            "declarations": [ wd.export() for wd in self.widgetdeclaration_set.all() ],
        }
    @classmethod
    def import_data(cls, data):
        try:
            w = WidgetDefinition.objects.get(url=data["url"], actual_frequency_url=data["actual_frequency_url"])
        except WidgetDefinition.DoesNotExist:
            w = WidgetDefinition(url=data["url"], actual_frequency_url=data["actual_frequency_url"])
        w.subcategory =  Subcategory.objects.get(name=data["subcategory"], category__name=data["category"])
        w.name = data["name"]
        w.expansion_hint = data["expansion_hint"]
        w.source_url = data["source_url"]
        w.actual_frequency = data["actual_frequency"]
        w.refresh_rate = data["refresh_rate"]
        w.sort_order = data["sort_order"]
        w.about = data["about"]
        w.save()
        tile_urls = []
        for t in data["tiles"]:
            TileDefinition.import_data(w, t)
            tile_urls.append(t["url"])
        for tile in w.tiledefinition_set.all():
            if tile.url not in tile_urls:
                tile.delete()
        for d in data["declarations"]:
            wd=WidgetDeclaration.import_data(w, d)
        for wd in w.widgetdeclaration_set.all():
            found = False
            for decl in data["declarations"]:
                if wd.location.url == decl["location"] and wd.frequency.url == decl["frequency"]:
                    found = True
                    break
            if not found:
                wd.delete()
        return w
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.actual_frequency)
    def data_last_updated(self, update=False):
        if self._lud_cache and not update:
            return self._lud_cache
        lud_statdata = StatisticData.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        lud_listdata = StatisticListItem.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        if lud_statdata is None:
            max_date = lud_listdata
        elif lud_listdata is None:
            max_date = lud_statdata
        else:   
            max_date = max(lud_statdata, lud_listdata)
        self._lud_cache = max_date
        return self._lud_cache
    class Meta:
        unique_together = (
            ("name", "actual_frequency"),
            ("url", "actual_frequency"),
            ("name", "actual_frequency_url"),
            ("url", "actual_frequency_url"),
            ("subcategory", "sort_order"),
        )
        ordering = ("subcategory", "sort_order")

class WidgetDeclaration(models.Model):
    definition = models.ForeignKey(WidgetDefinition)
    themes = models.ManyToManyField(Theme)
    frequency = models.ForeignKey(Frequency)
    location = models.ForeignKey(Location)
    def __unicode__(self):
        return "%s (%s:%s)" % (self.definition.name, self.location.name, self.frequency.name)
    def __getstate__(self):
        return self.definition.__getstate__()
    def export(self):
        return {
            "themes": [ t.url for t in self.themes.all() ],
            "frequency": self.frequency.url,
            "location": self.location.url,
        }
    @classmethod
    def import_data(cls, definition, data):
        try:
            decl = WidgetDeclaration.objects.get(definition=definition, 
                            location__url=data["location"],
                            frequency__url=data["frequency"])
        except WidgetDeclaration.DoesNotExist:
            decl = WidgetDeclaration(definition=definition)
            decl.location = Location.objects.get(url=data["location"])
            decl.frequency = Frequency.objects.get(url=data["frequency"])
            decl.save()
        decl.themes.clear()
        for t in data["themes"]:
            theme = Theme.objects.get(url=t)
            decl.themes.add(theme)
        return decl
    class Meta:
        unique_together = ( ("location", "frequency", "definition"),)
        ordering = ("location", "frequency", "definition")

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
    expansion =  models.BooleanField(default=False, help_text="A widget must have one and only one non-expansion tile")
    url = models.SlugField()
    sort_order = models.IntegerField(help_text="Note: The default (non-expansion) tile is always sorted first")
    # graph_def, map_def
    def __getstate__(self):
        state = {
            "type": self.tile_types[self.tile_type],
            "expansion": self.expansion,
        }
        if self.tile_type in (self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, self.PRIORITY_LIST, self.URGENCY_LIST):
            state["statistics"] = [ s.__getstate__() for s in self.statistic_set.all() ]
        if self.tile_type == self.GRAPH:
            pass # TODO
        if self.tile_type == self.MAP:
            pass # TODO
        return state
    def export(self):
        return {
            "tile_type": self.tile_type,
            "expansion": self.expansion,
            "url": self.url,
            "sort_order": self.sort_order,
            "statistics": [ s.export() for s in self.statistic_set.all() ],
        }
    @classmethod
    def import_data(cls, widget, data):
        try:
            t = TileDefinition.objects.get(widget=widget, url=data["url"])
        except TileDefinition.DoesNotExist:
            t = TileDeclaration(widget=widget, url=data["url"])
        t.tile_type = data["tile_type"]
        t.expansion = data["expansion"]
        t.sort_order = data["sort_order"]
        t.save()
        stat_urls = []
        for s in data["statistics"]:
            Statistic.import_data(t, s)
            stat_urls.append(s["url"])
        for stat in t.statistic_set.all():
            if stat.url not in stat_urls:
                stat.delete()
        return t
    def validate(self):
        """Validate Tile Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        # Number of statistics
        min_stat_count = 0
        max_stat_count = 20
        if self.tile_type == self.SINGLE_MAIN_STAT:
            min_stat_count = 1
        elif self.tile_type in (self.DOUBLE_MAIN_STAT,
                            self.PRIORITY_LIST, self.URGENCY_LIST):
            min_stat_count = 2
        elif self.tile_type in (self.LIST_OVERFLOW, self.GRAPH, self.MAP):
            max_stat_count = 0
        num_stats = self.statistic_set.all().count()
        if num_stats < min_stat_count:
            problems.append("Tile %s of Widget %s has %d statistics defined (minimum: %d)" % (self.url, self.widget.url, num_stats, min_stat_count))
        if num_stats > max_stat_count:
            problems.append("Tile %s of Widget %s has %d statistics defined (maximum: %d)" % (self.url, self.widget.url, num_stats, max_stat_count))
        # List overflow rules
        if self.tile_type == self.LIST_OVERFLOW:
            if not self.expansion:
                problems.append("Tile %s of Widget %s is of type List Overflow but is not an expansion tile" % (self.url, self.widget.url))
            else:
                try:
                    default_tile = self.widget.tiledefinition_set.get(expansion=False)
                    if default_tile.tile_type not in (self.PRIORITY_LIST, self.URGENCY_LIST):
                        problems.append("Tile %s of Widget %s is of type List Overflow, but the default tile is not a list tile" % (self.url, self.widget.url))
                except (TileDefinition.DoesNotExist, 
                        TileDefinition.MultipleObjectsReturned):
                    # Should already have been reported as an error higher up
                    pass
        # List tile should not have list statistics
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            for stat in self.statistic_set.all():
                if stat.is_list():
                    problems.append("Tile %s of Widget %s is a list tile and contains statistic %s, which is a list statistic. (Cannot have lists of lists)." % (self.url, self.widget.url, stat.url))
        # Validate all stats.
        for stat in self.statistic_set.all():
            problems.extend(stat.validate())
        return problems
    def __unicode__(self):
        if self.expansion:
            return "%s (expansion tile %d)" % (unicode(self.widget), self.sort_order)
        else:
            return "%s (default tile)" % (unicode(self.widget))
    class Meta:
        unique_together=[("widget", "sort_order"), ("widget", "url")]
        ordering=["widget", "expansion", "sort_order"]

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
        return [ c.__getstate__() for c in self.trafficlightscalecode_set.all() ]
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
   
class Statistic(models.Model):
    _lud_cache = None
    STRING = 1
    NUMERIC = 2
    STRING_KVL = 3
    NUMERIC_KVL = 4
    STRING_LIST = 5
    AM_PM = 6
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list", "am_pm" ]
    tile = models.ForeignKey(TileDefinition)
    name = models.CharField(max_length=80, blank=True)
    url = models.SlugField()
    name_as_label=models.BooleanField(default=True)
    stat_type = models.SmallIntegerField(choices=(
                    (STRING, stat_types[STRING]),
                    (NUMERIC, stat_types[NUMERIC]),
                    (STRING_KVL, stat_types[STRING_KVL]),
                    (NUMERIC_KVL, stat_types[NUMERIC_KVL]),
                    (STRING_LIST, stat_types[STRING_LIST]),
                    (AM_PM, stat_types[AM_PM]),
                ))
    traffic_light_scale = models.ForeignKey(TrafficLightScale, blank=True, null=True)
    icon_library = models.ForeignKey(IconLibrary, blank=True, null=True)
    trend = models.BooleanField(default=False)
    num_precision = models.SmallIntegerField(blank=True, null=True)
    unit_prefix = models.CharField(max_length="10", blank=True, null=True)
    unit_suffix = models.CharField(max_length="10", blank=True, null=True)
    unit_underfix = models.CharField(max_length="40", blank=True, null=True)
    unit_signed = models.BooleanField(default=False)
    sort_order = models.IntegerField()
    def clean(self):
        if not self.is_numeric():
            self.num_precision = None
            self.unit_prefix = None
            self.unit_suffix = None
            self.unit_underfix = None
            self.unit_signed = False
        if self.stat_type in (self.STRING_LIST, self.AM_PM):
            self.traffic_light_scale = None
            self.icon_library = None
        if self.is_list():
            name_as_label=True
    def validate(self):
        """Validate Tile Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        self.clean()
        self.save()
        problems = []
        if self.is_numeric():
            if self.num_precision is None:
                problems.append("Statistic %s of Widget %s is numeric, but has no precision set" % (self.url, self.tile.widget.url))
            elif self.num_precision < 0:
                problems.append("Statistic %s of Widget %s has negative precision" % (self.url, self.tile.widget.url))
        return problems
    def __unicode__(self):
        return "%s[%s]" % (self.tile,self.name)
    def is_numeric(self):
        return self.stat_type in (self.NUMERIC, self.NUMERIC_KVL)
    def is_list(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL,
                                self.STRING_LIST)
    def is_kvlist(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL)
    def initial_form_datum(self, sd):
        result = {}
        if self.is_numeric():
            if self.num_precision == 0:
                result["value"] = sd.intval
            else:
                result["value"] = sd.decval
        else:
            result["value"] = sd.strval
        if self.traffic_light_scale:
            result["traffic_light_code"] = sd.traffic_light_code.value
        if self.icon_library:
            result["icon_code"] = sd.icon_code.value
        if self.trend:
            result["trend"] = unicode(sd.trend)
        if self.is_list():
            if self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL):
                result["label"] = sd.keyval
            result["sort_order"] = sd.sort_order
        elif not self.name_as_label:
            result["label"] = sd.label
        return result
    def get_data(self):
        if self.is_list():
            return StatisticListItem.objects.filter(statistic=self)
        else:
            try:
                return StatisticData.objects.get(statistic=self)
            except StatisticData.DoesNotExist:
                return None
    def get_data_json(self):
        data = self.get_data()
        if self.is_list():
            return [ self.jsonise(datum) for datum in data ]
        else:
            return self.jsonise(data)
    def jsonise(self, datum):
        json = {}
        if datum:
            json["value"] = datum.value()
            if self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL):
                json["label"]=datum.keyval
            elif not self.name_as_label:
                json["label"]=datum.label
            if self.traffic_light_scale:
                json["traffic_light"]=datum.traffic_light_code.value
            if self.icon_library:
                json["icon"]=datum.icon_code.__getstate__()
            if self.trend:
                json["trend"]=datum.trend
        return json
    def initial_form_data(self):
        if self.is_list():
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
        if self.is_list():
            self._lud_cache = StatisticListItem.objects.filter(statistic=self).aggregate(lud=models.Max('last_updated'))['lud']
        else:
            try:
                self._lud_cache = StatisticData.objects.get(statistic=self).last_updated
            except StatisticData.DoesNotExist:
                self._lud_cache = None
                lud_statdata = None
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
            "name": self.name,
            "name_as_label": self.name_as_label,
            "url": self.url,
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
            state["trend"] = self.trend
            if self.traffic_light_scale:
                state["traffic_light_scale"] = self.traffic_light_scale.__getstate__()
            else:
                state["traffic_light_scale"] = None
            if self.icon_library:
                state["icon_library"] = self.icon_library.name
            else:
                state["icon_library"] = None
        return state
    class Meta:
        unique_together = [("tile", "name"), ("tile", "url")]
        ordering = [ "tile", "sort_order" ]

