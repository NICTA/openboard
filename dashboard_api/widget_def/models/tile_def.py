from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps

from widget_def.models.widget_definition import WidgetDefinition

# Create your models here.

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
    NEWSTICKER = 12
    GRAPH_SINGLE_STAT = 13
    GRID_SINGLE_STAT = 14
    MULTI_LIST_STAT = 15
    TAG_CLOUD = 16
    TIME_LINE = 17
    tile_types = [ "-", 
                "single_main_stat", "double_main_stat", 
                "priority_list", "urgency_list", "list_overflow", 
                "graph", "map", 
                "calendar", "grid", 
                "single_list_stat", 
                "newsfeed", "news_ticker",
                "graph_single_stat", "grid_single_stat",
                "multi_list_stat", "tag_cloud",
                "time_line", ]
    widget = models.ForeignKey(WidgetDefinition)
    tile_type = models.SmallIntegerField(choices=(
                    (SINGLE_MAIN_STAT, tile_types[SINGLE_MAIN_STAT]),
                    (DOUBLE_MAIN_STAT, tile_types[DOUBLE_MAIN_STAT]),
                    (SINGLE_LIST_STAT, tile_types[SINGLE_LIST_STAT]),
                    (MULTI_LIST_STAT, tile_types[MULTI_LIST_STAT]),
                    (PRIORITY_LIST, tile_types[PRIORITY_LIST]),
                    (URGENCY_LIST, tile_types[URGENCY_LIST]),
                    (LIST_OVERFLOW, tile_types[LIST_OVERFLOW]),
                    (GRAPH, tile_types[GRAPH]),
                    (GRAPH_SINGLE_STAT, tile_types[GRAPH_SINGLE_STAT]),
                    # (MAP, tile_types[MAP]),
                    (GRID, tile_types[GRID]),
                    (GRID_SINGLE_STAT, tile_types[GRID_SINGLE_STAT]),
                    (CALENDAR, tile_types[CALENDAR]),
                    (TIME_LINE, tile_types[TIME_LINE]),
                    (NEWSFEED, tile_types[NEWSFEED]),
                    (NEWSTICKER, tile_types[NEWSTICKER]),
                    (TAG_CLOUD, tile_types[TAG_CLOUD]),
                ))
    aspect = models.IntegerField(default=1)
    expansion =  models.BooleanField(default=False, help_text="A widget must have one and only one non-expansion tile")
    list_label_width= models.SmallIntegerField(blank=True, null=True,validators=[MinValueValidator(30), MaxValueValidator(100)])
    columns = models.SmallIntegerField(blank=True, null=True)
    url = models.SlugField()
    sort_order = models.IntegerField(help_text="Note: The default (non-expansion) tile is always sorted first")
    # graph_def, map_def
    def __getstate__(self):
        state = {
            "type": self.tile_types[self.tile_type],
            "expansion": self.expansion,
            "aspect": self.aspect,
        }
        if self.tile_type in (self.NEWSFEED, self.NEWSTICKER, 
                                self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, 
                                self.PRIORITY_LIST, self.URGENCY_LIST, self.CALENDAR, self.TIME_LINE,
                                self.MULTI_LIST_STAT, self.GRAPH_SINGLE_STAT, 
                                self.TAG_CLOUD):
            state["statistics"] = [ s.__getstate__() for s in self.statistic_set.all() ]
        if self.tile_type == self.GRID_SINGLE_STAT:
            state["statistics"] = []
            for s in self.statistic_set.all():
                if s.gridstatistic_set.count() == 0:
                    state["statistics"].append(s.__getstate__())
        if self.tile_type in (self.SINGLE_LIST_STAT, self.PRIORITY_LIST, self.URGENCY_LIST):
            if self.list_label_width:
                state["list_label_width"] = self.list_label_width
            else:
                state["list_label_width"] = 50
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            state["columns"] = self.columns
        if self.tile_type in (self.GRAPH, self.GRAPH_SINGLE_STAT):
            GraphDefinition = apps.get_app_config("widget_def").get_model("GraphDefinition")
            g = GraphDefinition.objects.get(tile=self)
            state["graph"] = g.__getstate__()
        if self.tile_type == self.MAP:
            pass # TODO
        if self.tile_type in (self.GRID, self.GRID_SINGLE_STAT):
            GridDefinition = apps.get_app_config("widget_def").get_model("GridDefinition")
            state["grid"] = GridDefinition.objects.get(tile=self).__getstate__()
        return state
    def export(self):
        exp = {
            "tile_type": self.tile_type,
            "expansion": self.expansion,
            "aspect": self.aspect,
            "url": self.url,
            "sort_order": self.sort_order,
            "columns": self.columns,
            "list_label_width": self.list_label_width,
            "statistics": [ s.export() for s in self.statistic_set.all() ],
        }
        if self.tile_type in (self.GRAPH, self.GRAPH_SINGLE_STAT):
            g = self.graphdefinition
            exp["graph"] = g.export()
        if self.tile_type in (self.GRID, self.GRID_SINGLE_STAT):
            g = self.griddefinition
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
        t.aspect = data.get("expansion", 1)
        t.list_label_widh = data.get("list_label_width")
        t.columns = data.get("columns")
        t.sort_order = data["sort_order"]
        t.clean()
        t.save()
        stat_urls = []
        Statistic = apps.get_app_config("widget_def").get_model("Statistic")
        for s in data["statistics"]:
            Statistic.import_data(t, s)
            stat_urls.append(s["url"])
        for stat in t.statistic_set.all():
            if stat.url not in stat_urls:
                stat.delete()
        GraphDefinition = apps.get_app_config("widget_def").get_model("GraphDefinition")
        GridDefinition = apps.get_app_config("widget_def").get_model("GridDefinition")
        GraphDefinition.import_data(t, data.get("graph"))
        GridDefinition.import_data(t, data.get("grid"))
        return t
    def clean(self):
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            if self.columns is None:
                self.columns = 1
        else:
            self.columns = None
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            if not self.list_label_width:
                self.list_label_width = 50
        elif self.tile_type in (self.SINGLE_LIST_STAT, self.MULTI_LIST_STAT):
            for stat in self.statistic_set.all():
                if stat.stat_type == stat.STRING_LIST:
                    self.list_label_width = 100
        else:
            self.list_label_width = None
    def validate(self):
        """Validate Tile Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        self.clean()
        self.save()
        problems = []
        # Number of statistics
        min_list_stat_count = 0
        max_list_stat_count = 0
        min_scalar_stat_count = 1
        max_scalar_stat_count = 40
        if self.tile_type == self.SINGLE_MAIN_STAT:
            max_scalar_stat_count = 5
        if self.tile_type == self.DOUBLE_MAIN_STAT:
            min_scalar_stat_count = 2
            max_scalar_stat_count = 2
        if self.tile_type in (self.LIST_OVERFLOW, self.GRAPH):
            min_scalar_stat_count = 0
            max_scalar_stat_count = 0
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            pass # Defaults all correct
        if self.tile_type == self.MAP:
            problems.append("Tile %s of Widget %s is of type 'map' which is not yet supported")
        if self.tile_type in (self.CALENDAR, self.SINGLE_LIST_STAT, 
                            self.NEWSFEED, self.NEWSTICKER, self.TAG_CLOUD, self.TIME_LINE):
            min_scalar_stat_count = 0
            max_scalar_stat_count = 0
            min_list_stat_count = 1
            max_list_stat_count = 1
        if self.tile_type == self.GRAPH_SINGLE_STAT:
            max_scalar_stat_count = 1
        if self.tile_type == self.MULTI_LIST_STAT:
            min_list_stat_count = 1
            max_list_stat_count = 4
            min_scalar_stat_count = 0
            max_scalar_stat_count = 1
        stats = self.statistic_set.all()
        scalar_stats = 0
        list_stats = 0
        for s in stats:
            if s.is_display_list():
                list_stats += 1
            else:
                scalar_stats += 1
        if scalar_stats < min_scalar_stat_count:
            problems.append("Tile %s of Widget %s has %d scalar (non-list) statistics defined (minimum: %d)" % (self.url, self.widget.url(), scalar_stats, min_scalar_stat_count))
        if scalar_stats > max_scalar_stat_count:
            problems.append("Tile %s of Widget %s has %d scalar (non-list) statistics defined (maximum: %d)" % (self.url, self.widget.url(), scalar_stats, max_scalar_stat_count))
        if list_stats < min_list_stat_count:
            problems.append("Tile %s of Widget %s has %d list statistics defined (minimum: %d)" % (self.url, self.widget.url(), list_stats, min_list_stat_count))
        if list_stats > max_list_stat_count:
            problems.append("Tile %s of Widget %s has %d list statistics defined (maximum: %d)" % (self.url, self.widget.url(), list_stats, max_list_stat_count))
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
                    elif default_tile.tile_type == self.NEWSTICKER:
                        pass #OK
                    else:
                        problems.append("Tile %s of Widget %s is of type List Overflow, but the default tile is not a list tile" % (self.url, self.widget.url()))
                except (TileDefinition.DoesNotExist, 
                        TileDefinition.MultipleObjectsReturned):
                    # NB This code will need to change if we start to support multiple default tiles.
                    # Should already have been reported as an error higher up
                    pass
        # only single_list_Stat tile should have list statistics
        if self.tile_type not in (self.MULTI_LIST_STAT, self.TAG_CLOUD, self.SINGLE_LIST_STAT, self.NEWSTICKER, self.NEWSFEED, self.CALENDAR, self.TIME_LINE):
            for stat in self.statistic_set.all():
                if stat.is_display_list():
                    problems.append("Tile %s of Widget %s is not a list stat tile, a calendar, tag cloud, news or time line tile and contains statistic %s, which is a list statistic. (Lists can only appear in tiles of the types listed)." % (self.url, self.widget.url(), stat.url))
        # Validate list_label_width:
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST):
            if not self.list_label_width:
                problems.append("Tile %s of Widget %s is of list type but does not have the list label width set" % (self.url, self.widget.url()))
            elif self.list_label_width > 85:
                problems.append("Tile %s of Widget %s is of list type has list label width greater than 85%%" % (self.url, self.widget.url()))
        elif self.tile_type in (self.SINGLE_LIST_STAT, self.MULTI_LIST_STAT):
            if not self.list_label_width:
                problems.append("Tile %s of Widget %s is of list type but does not have the list label width set" % (self.url, self.widget.url()))
            else:
                first_stat = True
                for stat in self.statistic_set.all():
                    if first_stat:
                        first_stat = False
                    else:
                        if self.tile_type == self.MULTI_LIST_STAT and not stat.is_display_list():
                            problems.append("Tile %s of Widget %s is a multi_list_stat tile and has a scalar (non-list) stat that isn't the first stat for the tile." % (self.url, self.widget.url()))
                    if stat.stat_type == stat.STRING_LIST:
                        if self.list_label_width != 100:
                            problems.append("Tile %s of Widget %s has a string list stat but does not have the list label width set to 100%%" % (self.url, self.widget.url()))
        if self.tile_type == self.NEWSFEED:
            for stat in self.statistic_set.all():
                if stat.stat_type != stat.STRING_KVL:
                    problems.append("Tile %s of Widget %s is a Newsfeed tile but has a non string kv list statistic" % (self.url, self.widget.url()))
        if self.tile_type == self.TAG_CLOUD:
            for stat in self.statistic_set.all():
                if stat.stat_type != stat.NUMERIC_KVL:
                    problems.append("Tile %s of Widget %s is a Newsfeed tile but has a non numeric kv list statistic" % (self.url, self.widget.url()))
        if self.tile_type == self.NEWSTICKER:
            for stat in self.statistic_set.all():
                if stat.stat_type != stat.STRING_LIST:
                    problems.append("Tile %s of Widget %s is a Newsticker tile but has a non string list statistic" % (self.url, self.widget.url()))
        # Must gave a graph if and only if a graph tile
        if self.tile_type in (self.GRAPH, self.GRAPH_SINGLE_STAT):
            try:
                g = self.graphdefinition
                problems.extend(g.validate())
            except models.ObjectDoesNotExist:
                problems.append("Tile %s of Widget %s is a graph tile but does not have a graph defined" % (self.url, self.widget.url()))
        else:
            try:
                self.graphdefinition.delete()
            except models.ObjectDoesNotExist:
                pass
        # Must have a grid if and only if a grid tile
        if self.tile_type in (self.GRID, self.GRID_SINGLE_STAT):
            try:
                g = self.griddefinition
                problems.extend(g.validate())
            except models.ObjectDoesNotExist:
                problems.append("Tile %s of Widget %s is a grid tile but does not have a grid defined" % (self.url, self.widget.url()))
        else:
            try:
                self.griddefinition.delete()
            except models.ObjectDoesNotExist:
                pass
        # Validate all stats.
        for stat in self.statistic_set.all():
            problems.extend(stat.validate())
        return problems
    def __unicode__(self):
        if self.expansion:
            return "%s (expansion tile %d)" % (unicode(self.widget), self.sort_order)
        else:
            return "%s (default tile %d)" % (unicode(self.widget), self.sort_order)
    class Meta:
        unique_together=[("widget", "sort_order"), ("widget", "url")]
        ordering=["widget", "expansion", "sort_order"]

