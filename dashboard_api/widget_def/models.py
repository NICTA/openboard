from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from widget_data.models import StatisticData, StatisticListItem, GraphData

# Create your models here.

class Theme(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Frequency(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    display_mode = models.BooleanField(default=True)
    actual_display = models.CharField(max_length=60, unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
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

def max_with_nulls(*args):
    maxargs = []
    for arg in args:
        if arg is not None:
            maxargs.append(arg)
    if len(maxargs) == 0:
        return None
    elif len(maxargs) == 1:
        return maxargs[0]
    else:
        return max(*maxargs)

class WidgetFamily(models.Model):
    subcategory = models.ForeignKey(Subcategory)
    name = models.CharField(max_length=60)
    subtitle = models.CharField(max_length=60, null=True, blank=True)
    url  = models.SlugField(unique=True)
    source_url = models.URLField(max_length=400)
    source_url_text = models.CharField(max_length=60)
    def __unicode__(self):
        if self.subtitle:
            return "%s (%s)" % (self.name, self.subtitle)
        else:
            return self.name
    def export(self):
        return {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "subtitle": self.subtitle,
            "name": self.name,
            "url": self.url,
            "source_url": self.source_url,
            "source_url_text": self.source_url_text,
            "definitions": [ wd.export() for wd in self.widgetdefinition_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            fam = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            fam = cls(url=data["url"])
        fam.subcategory =  Subcategory.objects.get(name=data["subcategory"], category__name=data["category"])
        if data.get("subtitle"):
            fam.subtitle = data["subtitle"]
        else:
            fam.subtitle = None
        fam.name = data["name"]
        fam.source_url = data["source_url"]
        fam.source_url_text = data["source_url_text"]
        fam.save()
        definitions = []
        for defn in data["definitions"]:
            WidgetDefinition.import_data(fam, defn)
            definitions.append((defn["actual_location_url"], defn["actual_frequency_url"]))
        for defn in fam.widgetdefinition_set.all():
            if (defn.actual_location.url, defn.actual_frequency.url) not in definitions:
                defn.delete()
        return fam

class WidgetDefinition(models.Model):
    _lud_cache = None
    family = models.ForeignKey(WidgetFamily)
    expansion_hint = models.CharField(max_length=80)
    actual_location = models.ForeignKey(Location)
    actual_frequency = models.ForeignKey(Frequency)
    refresh_rate = models.IntegerField(help_text="in seconds")
    sort_order = models.IntegerField(unique=True)
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
    def subcategory(self):
        return self.family.subcategory
    def url(self):
        return self.family.url
    def name(self):
        return self.family.name
    def subtitle(self):
        return self.family.subtitle
    def source_url(self):
        return self.family.source_url
    def __getstate__(self):
        return {
            "category": self.subcategory().category.name,
            "subcategory": self.subcategory().name,
            "name": self.name(),
            "subtitle": self.family.subtitle,
            "url": self.url(),
            "display": {
                "expansion_hint": self.expansion_hint,
                "tiles": [ tile.__getstate__() for tile in self.tiledefinition_set.all() ],
            },
            "source_url": self.source_url(),
            "source_url_text": self.family.source_url_text,
            "actual_frequency": self.actual_frequency.actual_display,
            "refresh_rate": self.refresh_rate,
            "about": self.about,
        }
    def export(self):
        return {
            "expansion_hint": self.expansion_hint,
            "actual_frequency_url": self.actual_frequency.url,
            "actual_location_url": self.actual_location.url,
            "refresh_rate": self.refresh_rate,
            "sort_order": self.sort_order,
            "about": self.about,
            "tiles": [ t.export() for t in self.tiledefinition_set.all() ],
            "declarations": [ wd.export() for wd in self.widgetdeclaration_set.all() ],
        }
    @classmethod
    def import_data(cls, family, data):
        try:
            w = WidgetDefinition.objects.get(family=family, actual_frequency__url=data["actual_frequency_url"], actual_location__url=data["actual_location_url"])
        except WidgetDefinition.DoesNotExist:
            w = WidgetDefinition(family=family,
                            actual_frequency=Frequency.objects.get(url=data["actual_frequency_url"]),
                            actual_location=Location.objects.get(url=data["actual_location_url"]))
        w.expansion_hint = data["expansion_hint"]
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
        return "%s (%s, %s)" % (self.family.name, self.actual_location.name, self.actual_frequency.name)
    def data_last_updated(self, update=False):
        if self._lud_cache and not update:
            return self._lud_cache
        lud_statdata = StatisticData.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        lud_listdata = StatisticListItem.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        lud_graphdata = GraphData.objects.filter(graph__tile__widget=self).aggregate(lud=models.Max("last_updated"))["lud"]
        self._lud_cache = max_with_nulls(lud_statdata, lud_listdata, lud_graphdata)
        return self._lud_cache
    class Meta:
        unique_together = (
            ("family", "actual_location", "actual_frequency"),
        )
        ordering = ("family__subcategory", "sort_order")

class WidgetDeclaration(models.Model):
    definition = models.ForeignKey(WidgetDefinition)
    theme = models.ForeignKey(Theme)
    frequency = models.ForeignKey(Frequency, limit_choices_to={
                            "display_mode": True
                    })
    location = models.ForeignKey(Location)
    def __unicode__(self):
        return "%s (%s:%s:%s)" % (self.definition.family.name, self.theme.name, self.location.name, self.frequency.name)
    def __getstate__(self):
        return self.definition.__getstate__()
    def export(self):
        return {
            "theme": self.theme.url,
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
            decl.theme = Theme.objects.get(url=data["theme"])
            decl.save()
        return decl
    class Meta:
        unique_together = ( ("theme", "location", "frequency", "definition"),)
        ordering = ("theme", "location", "frequency", "definition")

class TileDefinition(models.Model):
    SINGLE_MAIN_STAT = 1
    DOUBLE_MAIN_STAT = 2
    PRIORITY_LIST = 3
    URGENCY_LIST = 4
    LIST_OVERFLOW = 5
    GRAPH = 6
    MAP = 7
    CALENDAR = 8
    GRID = 9
    SINGLE_LIST_STAT = 10
    NEWSFEED = 11
    tile_types = [ "-", "single_main_stat", "double_main_stat", "priority_list", "urgency_list", "list_overflow", "graph", "map", "calendar", "grid", "single_list_stat", "newsfeed"]
    widget = models.ForeignKey(WidgetDefinition)
    tile_type = models.SmallIntegerField(choices=(
                    (SINGLE_MAIN_STAT, tile_types[SINGLE_MAIN_STAT]),
                    (DOUBLE_MAIN_STAT, tile_types[DOUBLE_MAIN_STAT]),
                    (SINGLE_LIST_STAT, tile_types[SINGLE_LIST_STAT]),
                    (PRIORITY_LIST, tile_types[PRIORITY_LIST]),
                    (URGENCY_LIST, tile_types[URGENCY_LIST]),
                    (LIST_OVERFLOW, tile_types[LIST_OVERFLOW]),
                    (GRAPH, tile_types[GRAPH]),
                    (CALENDAR, tile_types[CALENDAR]),
                    # (MAP, tile_types[MAP]),
                    (GRID, tile_types[GRID]),
                    (NEWSFEED, tile_types[NEWSFEED]),
                ))
    expansion =  models.BooleanField(default=False, help_text="A widget must have one and only one non-expansion tile")
    list_label_width= models.SmallIntegerField(blank=True, null=True,validators=[MinValueValidator(50), MaxValueValidator(100)])
    url = models.SlugField()
    sort_order = models.IntegerField(help_text="Note: The default (non-expansion) tile is always sorted first")
    # graph_def, map_def
    def __getstate__(self):
        state = {
            "type": self.tile_types[self.tile_type],
            "expansion": self.expansion,
        }
        if self.tile_type in (self.NEWSFEED, self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, self.PRIORITY_LIST, self.URGENCY_LIST, self.CALENDAR):
            state["statistics"] = [ s.__getstate__() for s in self.statistic_set.all() ]
        if self.tile_type in (self.SINGLE_LIST_STAT, self.PRIORITY_LIST, self.URGENCY_LIST):
            state["list_label_width"] = self.list_label_width
        if self.tile_type == self.GRAPH:
            g = GraphDefinition.objects.get(tile=self)
            state.update(g.__getstate__())
        if self.tile_type == self.MAP:
            pass # TODO
        if self.tile_type == self.GRID:
            state["grid"] = GridDefinition.objects.get(tile=self).__getstate__()
        return state
    def export(self):
        exp = {
            "tile_type": self.tile_type,
            "expansion": self.expansion,
            "url": self.url,
            "sort_order": self.sort_order,
            "list_label_width": self.list_label_width,
            "statistics": [ s.export() for s in self.statistic_set.all() ],
        }
        if self.tile_type == self.GRAPH:
            g = self.graphdefinition_set.get()
            exp["graph"] = g.export()
        if self.tile_type == self.GRID:
            g = self.griddefinition_set.get()
            exp["grid"] = g.export()
        return exp
    @classmethod
    def import_data(cls, widget, data):
        try:
            t = TileDefinition.objects.get(widget=widget, url=data["url"])
        except TileDefinition.DoesNotExist:
            t = TileDefinition(widget=widget, url=data["url"])
        t.tile_type = data["tile_type"]
        t.expansion = data["expansion"]
        t.list_label_widh = data.get("list_label_width")
        t.sort_order = data["sort_order"]
        t.save()
        stat_urls = []
        for s in data["statistics"]:
            Statistic.import_data(t, s)
            stat_urls.append(s["url"])
        for stat in t.statistic_set.all():
            if stat.url not in stat_urls:
                stat.delete()
        GraphDefinition.import_data(t, data.get("graph"))
        GridDefinition.import_data(t, data.get("grid"))
        return t
    def validate(self):
        """Validate Tile Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        # Number of statistics
        min_stat_count = 0
        max_stat_count = 40
        if self.tile_type in (self.NEWSFEED, self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.CALENDAR):
            min_stat_count = 1
            if self.tile_type in (self.NEWSFEED, self.SINGLE_LIST_STAT):
                max_stat_count = 1
        elif self.tile_type in (self.DOUBLE_MAIN_STAT,
                            self.PRIORITY_LIST, self.URGENCY_LIST):
            min_stat_count = 2
            if self.tile_type == self.DOUBLE_MAIN_STAT:
                max_stat_count = 2
        elif self.tile_type in (self.LIST_OVERFLOW, self.GRAPH, self.MAP):
            max_stat_count = 0
        num_stats = self.statistic_set.all().count()
        if num_stats < min_stat_count:
            problems.append("Tile %s of Widget %s has %d statistics defined (minimum: %d)" % (self.url, self.widget.url(), num_stats, min_stat_count))
        if num_stats > max_stat_count:
            problems.append("Tile %s of Widget %s has %d statistics defined (maximum: %d)" % (self.url, self.widget.url(), num_stats, max_stat_count))
        # List overflow rules
        if self.tile_type == self.LIST_OVERFLOW:
            if not self.expansion:
                problems.append("Tile %s of Widget %s is of type List Overflow but is not an expansion tile" % (self.url, self.widget.url()))
            else:
                try:
                    default_tile = self.widget.tiledefinition_set.get(expansion=False)
                    if default_tile.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
                        pass # OK
                    elif default_tile.tile_type == self.SINGLE_LIST_STAT:
                        pass #OK
                    elif default_tile.tile_type == self.NEWSFEED:
                        pass #OK
                    else:
                        problems.append("Tile %s of Widget %s is of type List Overflow, but the default tile is not a list tile" % (self.url, self.widget.url()))
                except (TileDefinition.DoesNotExist, 
                        TileDefinition.MultipleObjectsReturned):
                    # Should already have been reported as an error higher up
                    pass
        # only single_list_Stat tile should have list statistics
        if self.tile_type not in (self.SINGLE_LIST_STAT, self.NEWSFEED, self.CALENDAR):
            for stat in self.statistic_set.all():
                if stat.is_list():
                    problems.append("Tile %s of Widget %s is not a single_list_stat tile or a calendar tile and contains statistic %s, which is a list statistic. (Lists can only appear in single_list_stat and calendar tiles)." % (self.url, self.widget.url(), stat.url))
        # Validate list_label_width:
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            if not self.list_label_width:
                problems.append("Tile %s of Widget %s is of list type but does not have the list label width set" % (self.url, self.widget.url()))
            elif self.list_label_width > 80:
                problems.append("Tile %s of Widget %s is of list type has list label width greater than 80%%" % (self.url, self.widget.url()))
        elif self.tile_type == self.SINGLE_LIST_STAT:
            if not self.list_label_width:
                problems.append("Tile %s of Widget %s is of list type but does not have the list label width set" % (self.url, self.widget.url()))
            else:
                for stat in self.statistic_set.all():
                    if stat.stat_type == stat.STRING_LIST:
                        if self.list_label_width != 100:
                            problems.append("Tile %s of Widget %s has a string list stat but does not have the list label width set to 100%%" % (self.url, self.widget.url()))
        else:
            self.list_label_width = None
            self.save()
        if self.tile_type == self.NEWSFEED:
            for stat in self.statistic_set.all():
                if stat.stat_type != stat.STRING_KVL:
                    problems.append("Tile %s of Widget %s is a Newsfeed tile but has a non string kv list statistic" % (self.url, self.widget.url()))
        # Must gave a graph if and only if a graph tile
        if self.tile_type == self.GRAPH:
            try:
                g = GraphDefinition.objects.get(tile=self)
                problems.extend(g.validate())
            except GraphDefinition.DoesNotExist:
                problems.append("Tile %s of Widget %s is a graph tile but does not have a graph defined" % (self.url, self.widget.url()))
        else:
            self.graphdefinition_set.all().delete()
        # Must have a grid if and only if a grid tile
        if self.tile_type == self.GRID:
            try:
                g = GridDefinition.objects.get(tile=self)
                problems.extend(g.validate())
            except GridDefinition.DoesNotExist:
                problems.append("Tile %s of Widget %s is a grid tile but does not have a grid defined" % (self.url, self.widget.url()))
        else:
            self.griddefinition_set.all().delete()
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
    EVENT_LIST = 7
    stat_types = [ "-", "string", "numeric", "string_kv_list", "numeric_kv_list", "string_list", "am_pm" , "event_list" ]
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
                    (EVENT_LIST, stat_types[EVENT_LIST]),
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
    hyperlinkable = models.BooleanField(default=False)
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
        if self.is_list():
            name_as_label=True
        else:
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
    def is_list(self):
        return self.stat_type in (self.STRING_KVL, self.NUMERIC_KVL,
                                self.STRING_LIST, self.EVENT_LIST)
    def is_eventlist(self):
        return self.stat_type == (self.EVENT_LIST)
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
        if self.hyperlinkable:
            result["url"] = sd.url
        if self.is_list():
            if self.is_kvlist():
                result["label"] = sd.keyval
            elif self.is_eventlist():
                result["date"] = sd.datekey
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
            if self.is_kvlist():
                json["label"]=datum.keyval
            elif self.is_eventlist():
                json["date"]=datum.datekey.strftime("%Y-%m-%d")
            elif not self.name_as_label:
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
        if self.is_list():
            state["hyperlinkable"] = self.hyperlinkable
        return state
    class Meta:
        unique_together = [("tile", "name"), ("tile", "url")]
        ordering = [ "tile", "sort_order" ]

class GraphDefinition(models.Model):
        _lud_cache = None
        LINE = 1
        HISTOGRAM = 2
        BAR = 3
        PIE = 4
        graph_types = [ "-", "line", "histogram", "bar", "pie" ]
        NUMERIC = 1
        DATE = 2
        TIME = 3
        axis_types = [ "-", "numeric", "date", "time" ]
        tile = models.ForeignKey(TileDefinition, limit_choices_to={
                                'tile_type': TileDefinition.GRAPH
                                }, unique=True)
        heading = models.CharField(max_length=120, blank=True, null=True)
        graph_type = models.SmallIntegerField(choices=(
                        (LINE, graph_types[LINE]),
                        (HISTOGRAM, graph_types[HISTOGRAM]),
                        (BAR, graph_types[BAR]),
                        (PIE, graph_types[PIE]),
                    ))
        numeric_axis_label = models.CharField(max_length=120, blank=True, null=True)
        numeric_axis_always_show_zero = models.BooleanField(default=True)
        use_secondary_numeric_axis = models.BooleanField(default=False)
        secondary_numeric_axis_label = models.CharField(max_length=120, blank=True, null=True)
        secondary_numeric_axis_always_show_zero = models.BooleanField(default=True)
        horiz_axis_label = models.CharField(max_length=120, blank=True, null=True)
        horiz_axis_type = models.SmallIntegerField(choices=(
                        (0, axis_types[0]),
                        (NUMERIC, axis_types[NUMERIC]),
                        (DATE, axis_types[DATE]),
                        (TIME, axis_types[TIME]),
                    ), default=0)
        def widget(self):
            return self.tile.widget
        def use_numeric_axes(self):
            return self.graph_type in (self.LINE, self.HISTOGRAM, self.BAR)
        def use_clusters(self):
            return self.graph_type in (self.PIE, self.HISTOGRAM, self.BAR)
        def initial_form_data(self):
            return [ self.initial_form_datum(gd) for gd in self.get_data() ]
        def initial_form_datum(self, gd):
            result = {}
            result["value"] = gd.value
            result["dataset"] = gd.dataset
            if self.use_clusters():
                result["cluster"] = gd.cluster
            else:
                result["horiz_value"] = gd.horiz_value()
            return result
        def get_data(self):
            return GraphData.objects.filter(graph=self).natural_order(self)
        def get_last_datum(self, dataset, cluster=None):
            gd = None
            for gd in GraphData.objects.filter(graph=self, dataset__url=dataset, cluster__url=cluster).natural_order(self):
                pass
            return gd
        def data_last_updated(self, update=False):
            if self._lud_cache and not update:
                return self._lud_cache
            self._lud_cache = GraphData.objects.filter(graph=self).aggregate(lud=models.Max("last_updated"))["lud"]
            return self._lud_cache
        def jsonise_horiz_value(self, value):
            if self.horiz_axis_type == self.NUMERIC:
                return value
            elif self.horiz_axis_type == self.DATE:
                return value.strftime("%Y-%m-%d")
            elif self.horiz_axis_type == self.TIME:
                return value.strftime("%H-%M-%S")
            else:
                return None
        class Meta:
            ordering=('tile',)
        def __unicode__(self):
            return "%s:%s:graph" % (self.tile.widget.url(), self.tile.url)
        def export(self):
            return {
                "heading": self.heading,
                "graph_type": self.graph_type,
                "numeric_axis_label": self.numeric_axis_label,
                "numeric_axis_always_show_zero": self.numeric_axis_always_show_zero,
                "use_secondary_numeric_axis": self.use_secondary_numeric_axis,
                "secondary_numeric_axis_label": self.secondary_numeric_axis_label,
                "secondary_numeric_axis_always_show_zero": self.secondary_numeric_axis_always_show_zero,
                "horiz_axis_label": self.horiz_axis_label,
                "horiz_axis_type": self.horiz_axis_type,
                "clusters": { c.url: c.label for c in self.graphcluster_set.all() },
                "datasets": { d.url: d.export() for d in self.graphdataset_set.all() },
            }
        @classmethod
        def import_data(cls, tile, data):
            try:
                g = GraphDefinition.objects.get(tile=tile)
                if not data:
                    g.delete()
                    return
            except GraphDefinition.DoesNotExist:
                if data:
                    g = GraphDefinition(tile=tile)
                else:
                    return
            g.heading = data["heading"]
            g.graph_type = data["graph_type"]
            g.numeric_axis_label = data["numeric_axis_label"]
            g.numeric_axis_always_show_zero = data["numeric_axis_always_show_zero"]
            g.user_secondary_numeric_axis = data["use_secondary_numeric_axis"]
            g.secondary_numeric_axis_label = data["secondary_numeric_axis_label"]
            g.secondary_numeric_axis_always_show_zero = data["secondary_numeric_axis_always_show_zero"]
            g.horiz_axis_label = data["horiz_axis_label"]
            g.horiz_axis_type = data["horiz_axis_type"]
            g.save()
            cluster_urls = []
            for (c_url, c_label) in data["clusters"].items():
                GraphCluster.import_data(g, c_url, c_label)
                cluster_urls.append(c_url)
            for cluster in g.graphcluster_set.all():
                if cluster.url not in cluster_urls:
                    cluster.delete()
            dataset_urls = []
            for (d_url, dataset) in data["datasets"].items():
                GraphDataset.import_data(g, d_url, dataset)
                dataset_urls.append(d_url)
            for dataset in g.graphdataset_set.all():
                if dataset.url not in dataset_urls:
                    dataset.delete()
        def __getstate__(self):
            state = {
                "heading": self.heading,
                "graph_type": self.graph_types[self.graph_type],
            }
            if self.graph_type == self.LINE:
                state["vertical_axis"] = {
                    "label": self.numeric_axis_label,
                    "always_show_zero": self.numeric_axis_always_show_zero,
                }
                if self.use_secondary_numeric_axis:
                    state["secondary_vertical_axis"] = {
                        "label": self.secondary_numeric_axis_label,
                        "always_show_zero": self.secondary_numeric_axis_always_show_zero,
                    }
                state["horizontal_axis"] = {
                    "label": self.horiz_axis_label,
                    "type": self.axis_types[self.horiz_axis_type]
                }
                state["lines"] = { d.url: d.__getstate__() for d in self.graphdataset_set.all()}
            elif self.graph_type in (self.HISTOGRAM, self.BAR):
                state["numeric_axis"] = {
                    "label": self.numeric_axis_label,
                    "always_show_zero": self.numeric_axis_always_show_zero,
                }
                if self.use_secondary_numeric_axis:
                    state["secondary_numeric_axis"] = {
                        "label": self.secondary_numeric_axis_label,
                        "always_show_zero": self.secondary_numeric_axis_always_show_zero,
                    }
                state["clusters"] = { c.url: c.label for c in self.graphcluster_set.all() }
                state["bars"] = { d.url: d.__getstate__() for d in self.graphdataset_set.all()}
            elif self.graph_type == self.PIE:
                state["pies"] = { c.url: c.label for c in self.graphcluster_set.all() }
                state["sectors"] = { d.url: d.__getstate__() for d in self.graphdataset_set.all()}
            return state
        def clean(self):
            if not self.use_numeric_axes():
                self.numeric_axis_label = None
                self.use_secondary_numeric_axis = False
            if not self.use_clusters():
                self.graphcluster_set.all().delete()
            else:
                self.horiz_axis_label = None
                self.horiz_axis_type = 0
            if not self.use_secondary_numeric_axis:
                self.secondary_numeric_axis_label = None
        def validate(self):
            problems = []
            self.clean()
            self.save()
            for ds in self.graphdataset_set.all():
                ds.clean()
                ds.save()
            if self.use_clusters():
                if self.graphcluster_set.count() == 0:
                    problems.append("Graph for tile %s of widget %s is a %s graph but has no clusters defined" % (self.tile.url, self.widget.url(), self.graph_types[self.graph_type]))
            else:
                if self.horiz_axis_type == 0:
                    problems.append("Graph for tile %s of widget %s is a line graph but does not specify horizontal axis type" % (self.tile.url, self.tile.widget.url()))
            if self.graphdataset_set.count() == 0:
                problems.append("Graph for tile %s of widget %s has no datasets defined" % (self.tile.url, self.widget.url()))
            return problems

class GraphCluster(models.Model):
    # Histo/bar clusters or Pies
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField()
    label=models.CharField(max_length=80)
    def __unicode__(self):
        return self.url
    class Meta:
        unique_together = [("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "url" ]
    @classmethod
    def import_data(cls, g, url, label):
        try:
            c = GraphCluster.objects.get(graph=g, url=url)
        except GraphCluster.DoesNotExist:
            c = GraphCluster(graph=g, url=url)
        c.label = label
        c.save()

class GraphDataset(models.Model):
    # Lines, Bars, or Sectors
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField()
    label=models.CharField(max_length=80)
    colour = models.CharField(max_length=50)
    use_secondary_numeric_axis = models.BooleanField(default=False)
    class Meta:
        unique_together = [("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "url" ]
    def clean(self):
        if not self.graph.use_secondary_numeric_axis:
            self.use_secondary_numeric_axis = False
    def export(self):
        return {
            "label": self.label,
            "colour": self.colour,
            "use_secondary_numeric_axis": self.use_secondary_numeric_axis,
        }
    def __unicode__(self):
        return self.url
    @classmethod
    def import_data(cls, g, url, data):
        try:
            d = GraphDataset.objects.get(graph=g, url=url)
        except GraphDataset.DoesNotExist:
            d = GraphDataset(graph=g, url=url)
        d.label = data["label"]
        d.colour = data["colour"]
        d.use_secondary_numeric_axis = data["use_secondary_numeric_axis"]
        d.save()
    def __getstate__(self):
        state = {
            "label": self.label,
            "colour": self.colour,
        }
        if self.graph.use_secondary_numeric_axis:
            if self.graph.graph_type == self.graph.LINE:
                state["use_secondary_vertical_axis"] = self.use_secondary_numeric_axis
            else:
                state["use_secondary_numeric_axis"] = self.use_secondary_numeric_axis
        return state

class GridDefinition(models.Model):
    tile = models.ForeignKey(TileDefinition, limit_choices_to={
                                'tile_type': TileDefinition.GRID,
                                }, unique=True)
    corner_label = models.CharField(max_length=50, null=True, blank=True)
    show_column_headers = models.BooleanField(default=True)
    show_row_headers = models.BooleanField(default=True)
    def widget(self):
        return self.tile.widget
    def __unicode__(self):
        return "Grid for tile: %s" % unicode(self.tile)
    def export(self):
        return {
            "corner_label": self.corner_label,
            "show_column_headers": self.show_column_headers,
            "show_row_headers": self.show_row_headers,
            "columns": [ c.export() for c in self.gridcolumn_set.all() ],
            "rows": [ c.export() for c in self.gridrow_set.all() ],
        }
    def __getstate__(self):
        return {
            "corner_label": self.corner_label,
            "show_column_headers": self.show_column_headers,
            "show_row_headers": self.show_row_headers,
            "columns": [ c.__getstate__() for c in self.gridcolumn_set.all() ],
            "rows": [ c.__getstate__() for c in self.gridrow_set.all() ],
        }
    def validate(self):
        problems = []
        ncols = self.gridcolumn_set.count()
        nrows = self.gridrow_set.count()
        if ncols < 1 or ncols > 3:
            problems.append("Number of GridColumns must be at least one and at most 3 (not %d)" % ncols)
        if nrows < 1:
            problems.append("Number of GridRows must be at least one (not %d)" % nrows)
        if not self.tile.expansion:
            if self.tile.widget.family.subtitle:
                if self.show_column_headers:
                    max_rows = 2
                    situation = "a main tile with a subtitle and column headers"
                else:
                    max_rows = 3
                    situation = "a main tile with a subtitle and no column headers"
            else:
                if self.show_column_headers:
                    max_rows = 3
                    situation = "a main tile with no subtitle and column headers"
                else:
                    max_rows = 4
                    situation = "a main tile with no subtitle and no column headers"
            if nrows > max_rows:
                problems.append("Number of GridRows in %s cannot be more than %d (not %d)" % (situation, max_rows, nrows))
        required_stat_count = ncols * nrows
        stat_count = self.tile.statistic_set.count()
        gridstat_count = self.gridstatistic_set.count()
        if stat_count > gridstat_count:
            problems.append("Not all tile statistics have been defined in the grid")
        if stat_count > required_stat_count:
            problems.append("Not enough tile statistics to fill the grid")
        for gs in self.gridstatistic_set.all():
            if gs.row.grid != self:
                problems.append("Data mismatch in grid, row %s", gs.row.label)
            if gs.column.grid != self:
                problems.append("Data mismatch in grid, col %s", gs.column.label)
            if gs.statistic.tile != self.tile:
                problems.append("Data mismatch in grid, statistic %s", gs.statistic.url)
        return problems
    @classmethod
    def import_data(cls, tile, data):
        try:
            g = cls.objects.get(tile=tile)
            if not data:
                g.delete()
                return
        except cls.DoesNotExist:
            if data:
                g = cls(tile=tile)
            else:
                return 
        g.corner_label = data["corner_label"]
        g.show_column_headers = data["show_column_headers"]
        g.show_row_headers = data["show_row_headers"]
        g.save()
        columns = []
        for c in data["columns"]:
            col = GridColumn.import_data(g, c)
            columns.append(col.label)
        for col in g.gridcolumn_set.all():
            if col.label not in columns:
                col.delete()
        rows = []
        for r in data["rows"]:
            row = GridRow.import_data(g, r)
            rows.append(row.label)
        for row in g.gridrow_set.all():
            if row.label not in rows:
                row.delete()

class GridColumn(models.Model):
    grid = models.ForeignKey(GridDefinition)
    label = models.CharField(max_length=50)
    sort_order = models.IntegerField()
    def export(self):
        return {
            "label": self.label,
            "sort_order": self.sort_order,
        }
    def __getstate__(self):
        return {
            "label": self.label,
        }
    @classmethod
    def import_data(cls, grid, data):
        try:
            gc = cls.objects.get(grid=grid, label=data["label"])
        except cls.DoesNotExist:
            gc = cls(grid=grid, label=data["label"])
        gc.sort_order = data["sort_order"]
        gc.save()
        return gc
    class Meta:
        unique_together=( ("grid", "label"), ("grid", "sort_order") )
        ordering = ("grid", "sort_order")
    def __unicode__(self):
        return "Column %s" % self.label

class GridRow(models.Model):
    grid = models.ForeignKey(GridDefinition)
    label = models.CharField(max_length=50)
    sort_order = models.IntegerField()
    def export(self):
        return {
            "label": self.label,
            "sort_order": self.sort_order,
            "statistics": [ s.statistic.url for s in self.grid.gridstatistic_set.filter(row=self).order_by("column") ]
        }
    def __getstate__(self):
        return {
            "label": self.label,
            "statistics": [ s.__getstate__() for s in self.grid.gridstatistic_set.filter(row=self).order_by("column") ]
        }
    @classmethod
    def import_data(cls, grid, data):
        try:
            gr = cls.objects.get(grid=grid, label=data["label"])
        except cls.DoesNotExist:
            gr = cls(grid=grid, label=data["label"])
        gr.sort_order = data["sort_order"]
        gr.save()
        grid.gridstatistic_set.filter(row=gr).delete()
        for (col, sdata) in zip(grid.gridcolumn_set.all(), data["statistics"]):
            stat = Statistic.objects.get(tile=grid.tile, url = sdata)
            try:
                gs = GridStatistic.objects.get(grid=grid, row=gr, column=col, statistic=stat)
            except GridStatistic.DoesNotExist:
                gs = GridStatistic(grid=grid, row=gr, column=col, statistic=stat)
                gs.save()
        return gr
    class Meta:
        unique_together=( ("grid", "label"), ("grid", "sort_order") )
        ordering = ("grid", "sort_order")
    def __unicode__(self):
        return "Row %s" % self.label

class GridStatistic(models.Model):
    grid = models.ForeignKey(GridDefinition)
    column = models.ForeignKey(GridColumn)
    row = models.ForeignKey(GridRow)
    statistic = models.ForeignKey(Statistic)
    def export(self):
        return self.statistic.export()
    def __getstate__(self):
        return self.statistic.__getstate__()
    class Meta:
        unique_together = ( ("grid", "column", "row"), ("grid", "statistic") )
        ordering = ("grid", "row", "column")

