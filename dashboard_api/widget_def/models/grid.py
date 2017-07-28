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

from collections import OrderedDict

from django.db import models

from widget_def.models.tile_def import TileDefinition
from widget_def.models.statistic import Statistic
from widget_def.parametisation import parametise_label
from widget_def.model_json_tools import *

# Create your models here.

class GridDefinition(models.Model, WidgetDefJsonMixin):
    """
    Defines a grid for a grid type tile. Models a fixed-size rectangular table of statistics.

    May have column headers, or row headers, or both or neither.

    If a grid has both column and row headers, it may also have a corner label.
    """
    export_def = OrderedDict([
        ("tile", JSON_INHERITED("grid")),
        ("corner_label", JSON_ATTR()),
        ("show_column_headers", JSON_ATTR()),
        ("show_row_headers", JSON_ATTR()),
        ("columns", JSON_RECURSEDOWN("GridColumn", "columns", "grid", "label", app="widget_def")),
        ("rows", JSON_RECURSEDOWN("GridRow", "rows", "grid", "label", app="widget_def"))
    ])
    export_lookup = { "tile": "tile" }
    api_state_def = {
        "corner_label": JSON_ATTR(parametise=True),
        "show_column_headers": JSON_ATTR(),
        "show_row_headers": JSON_ATTR(),
        "columns": JSON_RECURSEDOWN("GridColumn", "columns", "grid", "label", app="widget_def"),
        "rows": JSON_RECURSEDOWN("GridRow", "rows", "grid", "label", app="widget_def"),
    }
    tile = models.OneToOneField(TileDefinition, related_name="grid", 
                                limit_choices_to=models.Q(
                                tile_type__in=(TileDefinition.GRID,
                                            TileDefinition.GRID_SINGLE_STAT)
                                ))
    corner_label = models.CharField(verbose_name="corner header", max_length=50, null=True, blank=True)
    show_column_headers = models.BooleanField(default=True)
    show_row_headers = models.BooleanField(default=True)
    def widget(self):
        return self.tile.widget
    def __unicode__(self):
        return "Grid for tile: %s" % unicode(self.tile)
    def validate(self):
        problems = []
        ncols = self.columns.count()
        nrows = self.rows.count()
        if ncols < 1:
            problems.append("Number of GridColumns must be at least one (not %d)" % ncols)
        if nrows < 1:
            problems.append("Number of GridRows must be at least one (not %d)" % nrows)
        required_stat_count = ncols * nrows
        stat_count = self.tile.statistics.count()
        gridstat_count = self.gridstatistic_set.count()
        nongrid_stat_count = stat_count - gridstat_count
        if self.tile.tile_type == self.tile.GRID_SINGLE_STAT:
            if nongrid_stat_count != 1:
                problems.append("Tiles of type grid_single_stat must have a single non-grid stat")
            else:
                first_stat = self.tile.statistics.all()[0]
                if first_stat.gridstatistic_set.count() != 0:
                    problems.append("Tiles of type grid_single_stat must have a single non-grid stat which is the statistic with the lowest sort order")
        else:
            if nongrid_stat_count != 0:
                problems.append("Not all tile statistics have been defined in the grid")
        if gridstat_count < required_stat_count:
            problems.append("Not enough tile statistics to fill the grid")
        for gs in self.gridstatistic_set.all():
            if gs.row.grid != self:
                problems.append("Data mismatch in grid, row %s", gs.row.label)
            if gs.column.grid != self:
                problems.append("Data mismatch in grid, col %s", gs.column.label)
            if gs.statistic.tile != self.tile:
                problems.append("Data mismatch in grid, statistic %s", gs.statistic.url)
        return problems

class GridColumn(models.Model, WidgetDefJsonMixin):
    export_def = {
        "grid": JSON_INHERITED("columns"),
        "label": JSON_ATTR(),
        "sort_order": JSON_IMPLIED()
    }
    export_lookup = { "grid": "grid", "label": "label" }
    api_state_def = {
        "header": JSON_ATTR(attribute="label", parametise=True)
    }
    grid = models.ForeignKey(GridDefinition, related_name="columns")
    label = models.CharField(verbose_name="header", max_length=50)
    sort_order = models.IntegerField()
    def widget(self):
        return self.grid.tile.widget
    class Meta:
        unique_together=( ("grid", "label"), ("grid", "sort_order") )
        ordering = ("grid", "sort_order")
    def __unicode__(self):
        return "Column %s" % self.label

class GridRow(models.Model, WidgetDefJsonMixin):
    class JSON_GRID_STAT(JSON_ATTR):
        def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
            if recurse_func == "export":
                export[key] = [ gs.statistic.url for gs in obj.grid_stats() ]
            else:
                export[key] = [ getattr(gs, recurse_func)(**kwargs) for gs in obj.grid_stats() ]
        def handle_import(self, js, cons_args, key, imp_kwargs, env):
            pass
        def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
            obj.grid.gridstatistic_set.filter(row=obj).delete()
            for (col, sdata) in zip(obj.grid.columns.all(), js[key]):
                stat = Statistic.objects.get(tile=obj.grid.tile, url=sdata)
                gs = GridStatistic(grid=obj.grid, row=obj, column=col, statistic=stat)
                gs.save()
    export_def = {
        "grid": JSON_INHERITED("rows"),
        "label": JSON_ATTR(),
        "sort_order": JSON_IMPLIED(),
        "statistics": JSON_GRID_STAT()
    }
    export_lookup = { "grid": "grid", "label": "label" }
    api_state_def = {
        "header": JSON_ATTR(attribute="label", parametise=True),
        "statistics": JSON_GRID_STAT()
    }
    grid = models.ForeignKey(GridDefinition, related_name="rows")
    label = models.CharField(verbose_name="header", max_length=50)
    sort_order = models.IntegerField()
    def widget(self):
        return self.grid.tile.widget
    def grid_stats(self):
        return self.grid.gridstatistic_set.filter(row=self).order_by("column")
    class Meta:
        unique_together=( ("grid", "label"), ("grid", "sort_order") )
        ordering = ("grid", "sort_order")
    def __unicode__(self):
        return "Row %s" % self.label

class GridStatistic(models.Model, WidgetDefJsonMixin):
    grid = models.ForeignKey(GridDefinition)
    column = models.ForeignKey(GridColumn)
    row = models.ForeignKey(GridRow)
    statistic = models.ForeignKey(Statistic)
    api_state_def = {
        "statistic": JSON_PASSDOWN(solo=True)
    }
    class Meta:
        unique_together = ( ("grid", "column", "row"), ("grid", "statistic") )
        ordering = ("grid", "row", "column")

