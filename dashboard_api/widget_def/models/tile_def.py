from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    tile_types = [ "-", "single_main_stat", "double_main_stat", "priority_list", "urgency_list", "list_overflow", "graph", "map", "calendar", "grid", "single_list_stat", "newsfeed", "news_ticker"]
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
                    (NEWSTICKER, tile_types[NEWSTICKER]),
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
        if self.tile_type in (self.NEWSFEED, self.NEWSTICKER, self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, self.PRIORITY_LIST, self.URGENCY_LIST, self.CALENDAR):
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
            g = self.graphdefinition
            exp["graph"] = g.export()
        if self.tile_type == self.GRID:
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
        if self.tile_type in (self.NEWSFEED, self.NEWSTICKER, self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.CALENDAR):
            min_stat_count = 1
            if self.tile_type in (self.NEWSFEED, self.NEWSTICKER, self.SINGLE_LIST_STAT):
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
                    elif default_tile.tile_type == self.NEWSTICKER:
                        pass #OK
                    else:
                        problems.append("Tile %s of Widget %s is of type List Overflow, but the default tile is not a list tile" % (self.url, self.widget.url()))
                except (TileDefinition.DoesNotExist, 
                        TileDefinition.MultipleObjectsReturned):
                    # Should already have been reported as an error higher up
                    pass
        # only single_list_Stat tile should have list statistics
        if self.tile_type not in (self.SINGLE_LIST_STAT, self.NEWSTICKER, self.NEWSFEED, self.CALENDAR):
            for stat in self.statistic_set.all():
                if stat.is_display_list():
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
        if self.tile_type == self.NEWSTICKER:
            for stat in self.statistic_set.all():
                if stat.stat_type != stat.STRING_LIST:
                    problems.append("Tile %s of Widget %s is a Newsticker tile but has a non string list statistic" % (self.url, self.widget.url()))
        # Must gave a graph if and only if a graph tile
        if self.tile_type == self.GRAPH:
            try:
                g = self.graphdefinition
                problems.extend(g.validate())
            except GraphDefinition.DoesNotExist:
                problems.append("Tile %s of Widget %s is a graph tile but does not have a graph defined" % (self.url, self.widget.url()))
        else:
            try:
                self.graphdefinition.delete()
            except GraphDefinition.DoesNotExist:
                pass
        # Must have a grid if and only if a grid tile
        if self.tile_type == self.GRID:
            try:
                g = self.griddefinition
                problems.extend(g.validate())
            except GridDefinition.DoesNotExist:
                problems.append("Tile %s of Widget %s is a grid tile but does not have a grid defined" % (self.url, self.widget.url()))
        else:
            try:
                self.griddefinition.delete()
            except GridDefinition.DoesNotExist:
                pass
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

