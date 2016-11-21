#   Copyright 2015,2016 CSIRO
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

import re

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps

from widget_def.models.widget_definition import WidgetDefinition
from widget_def.parametisation import parametise_label

# Create your models here.

class TileDefinition(models.Model):
    """
    Represents a tile or panel within a widget.

    Supported tile types are:

    main_stat:
        A tile with a number of main (non-display-list) :model:`widget_def.Statistic`s shown, and optionally 
        one or more secondary (non-display-list) statistics.

    text_template:
        A tile containing a text template into which non-list :model:`widget_def.Statistic` data can be inserted.  
        E.g. A sentence like "Of 12 services from 5 agencies, representing 65% of total traffic, 
        85% are online." where the numeric elements (including the '%' postfix character) are 
        (non-display-list) statistic data.

    single_list_stat:
        A tile containing a single :model:`widget_def.Statistic`, which must be a display list statistic. 

    multi_list_stat:
        A tile containing at least one and up to four display list :model:`widget_def.Statistic`s.  
        It may also contain a single non-display-list statistic, which must be the first statistic listed 
        if present.

    priority_list:
        A list of non-list :model:`widget_def.Statistic`s, to be displayed according to their sort_order. 

    urgency_list:
        A list of non-list :model:`widget_def.Statistic`s, ordered by traffic light value, 
        i.e. bad/red statistics first.

    list_overflow:
        If there is one default tile of type priority_list, urgency_list, newsfeed or single_list_stat, 
        then an expansion tile can be of type "list_overflow".  The tile should then be displayed with 
        all list items from the default tile list that didn't fit on the default tile. 

    calendar:
        A calendar tile - must contain only one :model:`widget_def.Statistic` which must be of event_list type.

    graph:
        A :model:`widget_def.Graph` is rendered in the tile.

    grid:
        :model:`widget_def.Statistic`s are displayed in a rectangular :model:`widget_def.Grid`.

    graph_single_stat:
        A :model: `widget_def.Graph` is rendered in the tile, along with one non-display-list 
        :model:`widget_def.Statistic`.

    grid_single_stat:
        Non-displa-list :model:`widget_def.Statistic`s are displayed in a rectangular :model:`widget_def.Grid`. 
        An additional non-display-list statistic is displayed outside the grid.

    newsfeed:
        A tile containing a single :model:`widget_def.Statistic` of type string_kv_list, rendered as a newsfeed
        with headlines (keys) and summaries (values).

    news_ticker:
        A tile containing a single :model:`widget_def.Statistic` of type string_list. 
        Displayed as a scrolling news feed.

    tag_cloud:
        A tile containing a tag-cloud. Contains a single numeric_kv_list :model:`widget_def.Statistic`, the 
        keys of which represent the tags to be displayed and the value of which represents the relative size 
        of the tags.

    time_line:
        A tile containing a time-line. Contains a single hierarchical_event_list :model:`widget_def.Statistic`.

    map:
        A map is rendered in the tile.  Tile must have a :model:`widget_def.GeoWindow` and one or more 
        :model:`widget_def.GeoDataset`s.

    text_block:
        Tile contains a block of raw HTML text to be served with the widget data. There can be at most one 
        text_block tile per widget.
    """
    SINGLE_MAIN_STAT = 1   # Deprecated
    DOUBLE_MAIN_STAT = 2   # Deprecated
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
    TEXT_TEMPLATE = 18
    TEXT_BLOCK = 19
    MAIN_STAT = 20
    tile_types = [ "-", 
                "single_main_stat (DO NOT USE)", "double_main_stat (DO NOT USE)", 
                "priority_list", "urgency_list", "list_overflow", 
                "graph", "map", 
                "calendar", "grid", 
                "single_list_stat", 
                "newsfeed", "news_ticker",
                "graph_single_stat", "grid_single_stat",
                "multi_list_stat", "tag_cloud",
                "time_line", "text_template", "text_block",
                "main_stat" ]
    widget = models.ForeignKey(WidgetDefinition, help_text="The widget the tile is part of")
    tile_type = models.SmallIntegerField(choices=(
# (SINGLE_MAIN_STAT, tile_types[SINGLE_MAIN_STAT]),
#                    (DOUBLE_MAIN_STAT, tile_types[DOUBLE_MAIN_STAT]),
                    (MAIN_STAT, tile_types[MAIN_STAT]),
                    (TEXT_TEMPLATE, tile_types[TEXT_TEMPLATE]),
                    (SINGLE_LIST_STAT, tile_types[SINGLE_LIST_STAT]),
                    (MULTI_LIST_STAT, tile_types[MULTI_LIST_STAT]),
                    (PRIORITY_LIST, tile_types[PRIORITY_LIST]),
                    (URGENCY_LIST, tile_types[URGENCY_LIST]),
                    (LIST_OVERFLOW, tile_types[LIST_OVERFLOW]),
                    (GRAPH, tile_types[GRAPH]),
                    (GRAPH_SINGLE_STAT, tile_types[GRAPH_SINGLE_STAT]),
                    (MAP, tile_types[MAP]),
                    (GRID, tile_types[GRID]),
                    (GRID_SINGLE_STAT, tile_types[GRID_SINGLE_STAT]),
                    (CALENDAR, tile_types[CALENDAR]),
                    (TIME_LINE, tile_types[TIME_LINE]),
                    (NEWSFEED, tile_types[NEWSFEED]),
                    (NEWSTICKER, tile_types[NEWSTICKER]),
                    (TAG_CLOUD, tile_types[TAG_CLOUD]),
                    (TEXT_BLOCK, tile_types[TEXT_BLOCK]),
                ), help_text="The type of tile")
    aspect = models.IntegerField(default=1, help_text="Front-end implementation-specific indicator of relative tile size within the widget.")
    expansion =  models.BooleanField(default=False, help_text="Whether the tile displays by default, or only when the widget is 'expanded'.")
    list_label_width= models.SmallIntegerField(blank=True, null=True,validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Relative width of the name column for a list.  May apply for main_stat, priority_list and urgency_list tiles, depending on front-end implementation.")
    columns = models.SmallIntegerField(blank=True, null=True, help_text="The number of columns to display a list (or lists) in. For single_list_stat, multi_list_stat, priority_list and urgency_list tiles.")
    template = models.CharField(max_length=512, blank=True, null=True, help_text="The text teplate for text_template tiles.  Reference statistics with '%{statistic_label}")
    url = models.SlugField("An identifier for the tile. Only appears in the API for graph tiles.")
    sort_order = models.IntegerField(help_text="How the tile is sorted within the widget. Note: The default (non-expansion) tile is always sorted first")
    geo_window = models.ForeignKey("GeoWindow", null=True, blank=True, help_text="For map tiles.  Describes the geospatial coordinates the map must cover.")
    geo_datasets = models.ManyToManyField("GeoDataset", blank=True, help_text="For map tiles. The geodatasets to display on the map")
    main_stat_count = models.SmallIntegerField(blank=True, null=True, help_text="For main_stat tiles. The number of Statistics that are 'main' statistics. The remainder are 'secondary'. The main statistics are the ones that are sorted first within the tile.")
    # graph_def, map_def
    def __getstate__(self, view=None):
        state = {
            "type": self.tile_types[self.tile_type],
            "expansion": self.expansion,
            "aspect": self.aspect,
        }
        if self.tile_type in (self.NEWSFEED, self.NEWSTICKER, 
                                self.SINGLE_LIST_STAT, self.SINGLE_MAIN_STAT, self.DOUBLE_MAIN_STAT, self.MAIN_STAT,
                                self.PRIORITY_LIST, self.URGENCY_LIST, self.CALENDAR, self.TIME_LINE,
                                self.MULTI_LIST_STAT, self.GRAPH_SINGLE_STAT, self.TEXT_TEMPLATE, 
                                self.TAG_CLOUD):
            state["statistics"] = [ s.__getstate__(view) for s in self.statistic_set.all() ]
        if self.tile_type == self.GRID_SINGLE_STAT:
            state["statistics"] = []
            for s in self.statistic_set.all():
                if s.gridstatistic_set.count() == 0:
                    state["statistics"].append(s.__getstate__(view))
        elif self.tile_type in (self.SINGLE_LIST_STAT, self.PRIORITY_LIST, self.URGENCY_LIST):
            if self.list_label_width:
                state["list_label_width"] = self.list_label_width
            else:
                state["list_label_width"] = 50
        if self.tile_type == self.TEXT_TEMPLATE:
            state["template"] = parametise_label(self.widget, view, self.template)
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST, self.MULTI_LIST_STAT, self.SINGLE_LIST_STAT):
            state["columns"] = self.columns
        if self.tile_type in (self.GRAPH, self.GRAPH_SINGLE_STAT):
            GraphDefinition = apps.get_app_config("widget_def").get_model("GraphDefinition")
            g = GraphDefinition.objects.get(tile=self)
            state["graph"] = g.__getstate__(view)
        if self.tile_type == self.MAP:
            state["map"] = {
                "url": self.url,
                "window": self.geo_window.__getstate__(view),
                "layers": [ ds.__getstate__(view=view,parametisation=self.widget.paremetisation) for ds in self.geo_datasets.all() ],
            }
        if self.tile_type in (self.GRID, self.GRID_SINGLE_STAT):
            GridDefinition = apps.get_app_config("widget_def").get_model("GridDefinition")
            state["grid"] = GridDefinition.objects.get(tile=self).__getstate__(view)
        if self.tile_type == self.MAIN_STAT:
            state["main_stat_count"] = self.main_stat_count
        return state
    def export(self):
        exp = {
            "tile_type": self.tile_type,
            "expansion": self.expansion,
            "aspect": self.aspect,
            "url": self.url,
            "template": self.template,
            "sort_order": self.sort_order,
            "columns": self.columns,
            "list_label_width": self.list_label_width,
            "statistics": [ s.export() for s in self.statistic_set.all() ],
            "geo_window": None,
            "geo_datasets": [ ds.url for ds in self.geo_datasets.all() ],
        }
        if self.tile_type == self.SINGLE_MAIN_STAT:
            exp["tile_type"] = self.MAIN_STAT
            exp["main_stat_count"] = 1
        elif self.tile_type == self.DOUBLE_MAIN_STAT:
            exp["tile_type"] = self.MAIN_STAT
            exp["main_stat_count"] = 2
        elif self.tile_type == self.MAIN_STAT:
            exp["main_stat_count"] = self.main_stat_count
        if self.geo_window:
            exp["geo_window"] = self.geo_window.name
        if self.tile_type in (self.GRAPH, self.GRAPH_SINGLE_STAT):
            try:
                g = self.graphdefinition
                exp["graph"] = g.export()
            except models.ObjectDoesNotExist:
                exp["graph"] = None
        if self.tile_type in (self.GRID, self.GRID_SINGLE_STAT):
            try:
                g = self.griddefinition
                exp["grid"] = g.export()
            except models.ObjectDoesNotExist:
                exp["grid"] = None
        return exp
    @classmethod
    def import_data(cls, widget, data):
        try:
            t = TileDefinition.objects.get(widget=widget, url=data["url"])
        except TileDefinition.DoesNotExist:
            t = TileDefinition(widget=widget, url=data["url"])
        t.tile_type = data["tile_type"]
        if t.tile_type == cls.SINGLE_MAIN_STAT:
            t.tile_type = cls.MAIN_STAT
            t.main_stat_count = 1
        elif t.tile_type == cls.DOUBLE_MAIN_STAT:
            t.tile_type = cls.MAIN_STAT
            t.main_stat_count = 2
        elif t.tile_type == cls.MAIN_STAT:
            t.main_stat_count = data["main_stat_count"]
        t.expansion = data["expansion"]
        t.aspect = data.get("aspect", 1)
        t.list_label_width = data.get("list_label_width")
        t.template = data.get("template")
        t.columns = data.get("columns")
        t.sort_order = data["sort_order"]
        GeoWindow = apps.get_app_config("widget_def").get_model("GeoWindow")
        GeoDataset = apps.get_app_config("widget_def").get_model("GeoDataset")
        if data.get("geo_window"):
            t.geo_window = GeoWindow.objects.get(name=data["geo_window"])
        else:
            t.geo_window = None
        t.clean()
        t.save()
        t.geo_datasets.clear()
        if "geo_datasets" in data:
            for ds in data["geo_datasets"]:
                t.geo_datasets.add(GeoDataset.objects.get(url=ds))
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
        if self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST, self.SINGLE_LIST_STAT, self.MULTI_LIST_STAT):
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
        if self.tile_type != self.MAIN_STAT:
            self.main_stat_count = None
        if self.tile_type != self.TEXT_TEMPLATE:
            self.template = None
        if self.tile_type != self.MAP:
            self.geo_window = None
            if self.id:
                self.geo_datasets.clear()
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
            problems.append("Tile %s of Widget %s is 'single_main_stat' type.  This tile type is now deprecated.  Use 'main_stat' tile type with main_stat_count=1" % (self.url, self.widget.url()))
            max_scalar_stat_count = 5
        elif self.tile_type == self.DOUBLE_MAIN_STAT:
            problems.append("Tile %s of Widget %s is 'double_main_stat' type.  This tile type is now deprecated.  Use 'main_stat' tile type with main_stat_count=2" % (self.url, self.widget.url()))
            min_scalar_stat_count = 2
            max_scalar_stat_count = 2
        elif self.tile_type == self.MAIN_STAT:
            if self.main_stat_count is None or self.main_stat_count < 1:
                problems.append("Tile %s of Widget %s is 'main_stat' type but main_stat_count is not set or less than one." % (self.url, self.widget.url()))
            min_scalar_stat_count = self.main_stat_count
        elif self.tile_type in (self.LIST_OVERFLOW, self.GRAPH):
            min_scalar_stat_count = 0
            max_scalar_stat_count = 0
        elif self.tile_type in (self.PRIORITY_LIST, self.URGENCY_LIST, self.TEXT_TEMPLATE):
            min_scalar_stat_count = 0
        elif self.tile_type == self.MAP:
            min_scalar_stat_count = 0
            max_scalar_stat_count = 0
        elif self.tile_type in (self.CALENDAR, self.SINGLE_LIST_STAT, 
                            self.NEWSFEED, self.NEWSTICKER, self.TAG_CLOUD, self.TIME_LINE):
            min_scalar_stat_count = 0
            max_scalar_stat_count = 0
            min_list_stat_count = 1
            max_list_stat_count = 1
        elif self.tile_type == self.GRAPH_SINGLE_STAT:
            max_scalar_stat_count = 1
        elif self.tile_type == self.MULTI_LIST_STAT:
            min_list_stat_count = 1
            max_list_stat_count = 4
            min_scalar_stat_count = 0
            max_scalar_stat_count = 1
        elif self.tile_type == self.TEXT_BLOCK:
            max_scalar_stat_count = 0
            min_scalar_stat_count = 0
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
        # Validate template
        if self.tile_type == self.TEXT_TEMPLATE:
            if not self.template:
                problems.append("Tile %s of Widget %s is a text template tile but does not have a template defined" % (self.url, self.widget.url()))
            else:
                referenced_urls = []
                references = re.findall(r'%\{\w+\}', self.template)
                start_refs = re.findall(r'%\{', self.template)
                if len(start_refs) > len(references):
                    problems.append("Tile %s of Widget %s has an invalid text template: %s" % (self.url, self.widget.url(), self.template))
                Statistic = apps.get_app_config("widget_def").get_model("Statistic")
                for reference in references:
                    m = re.match(r'%\{(?P<ref>\w+)\}', reference)
                    ref = m.group("ref")
                    try:
                        Statistic.objects.get(tile=self, url=ref)
                        referenced_urls.append(ref)
                    except Statistic.DoesNotExist:
                        problems.append("Text template of tile %s of Widget %s references statistic %s which is not defined" % (self.url, self.widget.url(), ref))
                for stat in self.statistic_set.all():
                    if stat.url not in referenced_urls:
                        problems.append("Text template of tile %s of Widget %s does not reference defined statistic %s" % (self.url, self.widget.url(), stat.url))
        # Validate Map
        if self.tile_type == self.MAP:
            if not self.geo_window:
                problems.append("No Geo-Window defined for map type tile %s of Widget %s" % (self.url, self.widget.url()))
            if self.geo_datasets.count() == 0:
                problems.append("No Geo-Datasets defined for map type tile %s of Widget %s" % (self.url, self.widget.url()))
            for ds in self.geo_datasets.all():
                problems.extend(ds.validate())
        # Validate all stats.
        stat_names = []
        for stat in self.statistic_set.all():
            problems.extend(stat.validate())
            if stat.name in stat_names:
                problems.append("Multiple statistics with name '%s' in tile %s of Widget %s" % (stat.name, self.url, self.widget.url()))
            elif stat.name:
                stat_names.append(stat.name)
        return problems
    def __unicode__(self):
        if self.expansion:
            return "%s (%s - expansion tile %d)" % (unicode(self.widget), self.url, self.sort_order)
        else:
            return "%s (%s - default tile %d)" % (unicode(self.widget), self.url, self.sort_order)
    class Meta:
        unique_together=[("widget", "sort_order"), ("widget", "url")]
        ordering=["widget", "expansion", "sort_order"]

