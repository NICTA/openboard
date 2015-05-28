from django.db import models

from widget_def.models.tile_def import TileDefinition
from widget_def.models.statistic import Statistic

# Create your models here.

class GridDefinition(models.Model):
    tile = models.OneToOneField(TileDefinition, limit_choices_to={
                                'tile_type': TileDefinition.GRID,
                                })
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
        nongrid_stat_count = stat_count - gridstat_count
        if self.tile.tile_type == self.tile.GRID_SINGLE_STAT:
            if nongrid_stat_count != 1:
                problems.append("Tiles of type grid_single_stat must have a single non-grid stat")
            else:
                first_stat = self.tile.statistic_set.all()[0]
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

