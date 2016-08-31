#   Copyright 2015,2016 NICTA
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

from django.db import models

from widget_data.models import GraphData, GraphDatasetData
from widget_def.models.graphbase import GraphClusterBase
from widget_def.models.tile_def import TileDefinition
from widget_def.parametisation import parametise_label, resolve_pval

# Create your models here.

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
        DATETIME = 4
        axis_types = [ "-", "numeric", "date", "time", "datetime" ]
        tile = models.OneToOneField(TileDefinition, limit_choices_to=models.Q(
                                tile_type__in=(TileDefinition.GRAPH, TileDefinition.GRAPH_SINGLE_STAT)
                                ))
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
        cluster_label = models.CharField(max_length=120, default="cluster", help_text="Not used for line graphs")
        dataset_label = models.CharField(max_length=120, default="dataset")
        dynamic_clusters = models.BooleanField(default=False)
        horiz_axis_label = models.CharField(max_length=120, blank=True, null=True)
        horiz_axis_type = models.SmallIntegerField(choices=(
                        (0, axis_types[0]),
                        (NUMERIC, axis_types[NUMERIC]),
                        (DATE, axis_types[DATE]),
                        (TIME, axis_types[TIME]),
                        (DATETIME, axis_types[DATETIME]),
                    ), default=0)
        def widget(self):
            return self.tile.widget
        def numeric_axis_name(self):
            if self.graph_type == self.LINE:
                return "vertical_axis"
            else:
                return "numeric_axis"
        def clusters(self, pval=None):
            if self.dynamic_clusters:
                return self.dynamicgraphcluster_set.filter(pval=pval)
            else:
                return self.graphcluster_set.all()
        def is_histogram(self):
            return self.graph_type in (self.BAR, self.HISTOGRAM)
        def use_numeric_axes(self):
            return self.graph_type in (self.LINE, self.HISTOGRAM, self.BAR)
        def use_clusters(self):
            return self.graph_type in (self.PIE, self.HISTOGRAM, self.BAR)
        def initial_form_data(self, pval=None, view=None):
            return [ self.initial_form_datum(gd) for gd in self.get_data(view=view,pval=pval) ]
        def initial_form_datum(self, gd):
            result = {}
            result["value"] = gd.value
            result["dataset"] = gd.dataset
            if self.use_clusters() and not self.dynamic_clusters:
                result["cluster"] = gd.cluster
            else:
                result["horiz_value"] = gd.horiz_value()
            if gd.dataset.use_error_bars:
                result["err_valmin"] = gd.err_valmin
                result["err_valmax"] = gd.err_valmax
            return result
        def initial_override_form_data(self, pval=None):
            result = {}
            # TODO: dynamic cluster definition
            for d in self.graphdataset_set.filter(dynamic_label=True):
                try:
                    dat = GraphDatasetData.objects.get(dataset=d,
                            param_value=pval)
                    result["dataset_%s" % d.url] = dat.display_name  
                except GraphDatasetData.DoesNotExist:
                    result["dataset_%s" % d.url] = d.label
            return result
        def get_data(self, view=None, pval=None):
            pval = resolve_pval(self.widget().parametisation, view=view, pval=pval)
            return GraphData.objects.filter(graph=self,param_value=pval).natural_order(self)
        def get_last_datum(self, dataset, cluster=None, pval=None):
            return GraphData.objects.filter(graph=self, 
                                dataset__url=dataset, 
                                param_value=pval,
                                cluster__url=cluster).natural_order(self).last()
        def data_last_updated(self, update=False, view=None, pval=None):
            pval = resolve_pval(self.widget().parametisation, view=view, pval=pval)
            if pval:
                if self._lud_cache and self._lud_cache.get(pval.id) and not update:
                    return self._lud_cache[pval.id]
                if not self._lud_cache:
                    self._lud_cache = {}
                self._lud_cache[pval.id] = GraphData.objects.filter(graph=self,param_value=pval).aggregate(lud=models.Max("last_updated"))["lud"]
                return self._lud_cache[pval.id]
            else:
                if self._lud_cache and not update:
                    return self._lud_cache
                self._lud_cache = GraphData.objects.filter(graph=self,param_value__isnull=True).aggregate(lud=models.Max("last_updated"))["lud"]
                return self._lud_cache
        def jsonise_horiz_value(self, value):
            if self.horiz_axis_type == self.NUMERIC:
                return value
            elif self.horiz_axis_type == self.DATE:
                return value.strftime("%Y-%m-%d")
            elif self.horiz_axis_type == self.TIME:
                return value.strftime("%H:%M:%S")
            elif self.horiz_axis_type == self.DATETIME:
                return value.strftime("%Y-%m-%dT%H:%M:%S")
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
                "cluster_label": self.cluster_label,
                "dataset_label": self.dataset_label,
                "display_options": self.graphdisplayoptions.export(),
                "dynamic_clusters": self.dynamic_clusters,
                "clusters": [ c.export() for c in self.graphcluster_set.all() ],
                "datasets": [ d.export() for d in self.graphdataset_set.all() ],
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
            g.cluster_label = data.get("cluster_label", "cluster")
            g.dataset_label = data.get("dataset_label", "dataset")
            g.dynamic_clusters = data.get("dynamic_clusters", False)
            g.save()
            GraphDisplayOptions.import_data(g, data.get("display_options"))
            cluster_urls = []
            for c_data in data["clusters"]:
                GraphCluster.import_data(g, c_data)
                cluster_urls.append(c_data["url"])
            for cluster in g.graphcluster_set.all():
                if cluster.url not in cluster_urls:
                    cluster.delete()
            dataset_urls = []
            for dataset in data["datasets"]:
                GraphDataset.import_data(g, dataset)
                dataset_urls.append(dataset["url"])
            for dataset in g.graphdataset_set.all():
                if dataset.url not in dataset_urls:
                    dataset.delete()
        def __getstate__(self, view=None):
            state = {
                "heading": parametise_label(self.widget(), view, self.heading),
                "graph_type": self.graph_types[self.graph_type],
                "label": self.tile.url,
                "display_options": self.graphdisplayoptions.__getstate__(self.graph_type),
            }
            if self.graph_type == self.LINE:
                state["vertical_axis"] = {
                    "name": parametise_label(self.widget(), view, self.numeric_axis_label),
                    "always_show_zero": self.numeric_axis_always_show_zero,
                }
                if self.use_secondary_numeric_axis:
                    state["secondary_vertical_axis"] = {
                        "name": parametise_label(self.widget(), view, self.secondary_numeric_axis_label),
                        "always_show_zero": self.secondary_numeric_axis_always_show_zero,
                    }
                state["horizontal_axis"] = {
                    "name": parametise_label(self.tile.widget, view, self.horiz_axis_label),
                    "type": self.axis_types[self.horiz_axis_type]
                }
                state["line_label"] = self.dataset_label
                state["lines"] = [ d.__getstate__(view) for d in self.graphdataset_set.all() ]
            elif self.graph_type in (self.HISTOGRAM, self.BAR):
                state["numeric_axis"] = {
                    "name": parametise_label(self.tile.widget, view, self.numeric_axis_label),
                    "always_show_zero": self.numeric_axis_always_show_zero,
                }
                if self.use_secondary_numeric_axis:
                    state["secondary_numeric_axis"] = {
                        "name": parametise_label(self.tile.widget, view, self.secondary_numeric_axis_label),
                        "always_show_zero": self.secondary_numeric_axis_always_show_zero,
                    }
                state["cluster_label"] = self.cluster_label
                state["bar_label"] = self.dataset_label
                state["dynamic_clusters"] = self.dynamic_clusters
                if not self.dynamic_clusters:
                    state["clusters"] = [ c.__getstate__(view) for c in self.graphcluster_set.all() ]
                state["bars"] = [ d.__getstate__(view) for d in self.graphdataset_set.all()]
            elif self.graph_type == self.PIE:
                state["pie_label"] = self.cluster_label
                state["dynamic_pies"] = self.dynamic_clusters
                if not self.dynamic_clusters:
                    state["pies"] = [ c.__getstate__(view) for c in self.graphcluster_set.all() ]
                state["sectors"] = [ d.__getstate__(view) for d in self.graphdataset_set.all()]
            return state
        def clean(self):
            if not self.use_numeric_axes():
                self.numeric_axis_label = None
                self.use_secondary_numeric_axis = False
            if not self.use_clusters() or self.dynamic_clusters:
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
            try:
                self.graphdisplayoptions
            except GraphDisplayOptions.DoesNotExist:
                GraphDisplayOptions.create_default(self)
            problems.extend(self.graphdisplayoptions.validate())
            for ds in self.graphdataset_set.all():
                ds.clean()
                ds.save()
            if self.use_clusters():
                if self.graphcluster_set.count() == 0 and not self.dynamic_clusters:
                    problems.append("Graph for tile %s of widget %s is a %s graph but has no clusters defined" % (self.tile.url, self.widget().url(), self.graph_types[self.graph_type]))
            else:
                if self.dynamic_clusters:
                    problems.append("Graph for tile %s of widget %s is a line graph but has dynamic_clusters set" % (self.tile.url, self.tile.widget.url()))
                if self.horiz_axis_type == 0:
                    problems.append("Graph for tile %s of widget %s is a line graph but does not specify horizontal axis type" % (self.tile.url, self.tile.widget.url()))
            if self.graphdataset_set.count() == 0:
                problems.append("Graph for tile %s of widget %s has no datasets defined" % (self.tile.url, self.widget().url()))
            if self.graphdataset_set.filter(use_error_bars=True).count() > 0 and not self.use_numeric_axes():
                problems.append("Pie chart for tile %s of widget %s uses error bars on a dataset." % (self.tile.url, self.widget().url()))
            return problems

class PointColourMap(models.Model):
    label=models.CharField(verbose_name="name", max_length=50, unique=True)
    decimal_places = models.SmallIntegerField(default=0)
    class Meta:
        ordering = ('label',)
    def __unicode__(self):
        return self.label
    def export(self):
        return {
            "label": self.label,
            "decimal_places": self.decimal_places,
            "map": [ r.export() for r in self.pointcolourrange_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            m = PointColourMap.objects.get(label=data["label"])
            m.decimal_places = data["decimal_places"]
        except PointColourMap.DoesNotExist:
            m = PointColourMap(label=data["label"], decimal_places=data["decimal_places"])
        m.save()
        m.pointcolourrange_set.all().delete()
        for r in data["map"]:
            PointColourRange.import_data(m, r)
        return m
    def __getstate__(self):
        data = {
            "name": self.label,
            "map": [ self.pointcolourrange_set.get(min_value_dec__isnull=True, min_value_int__isnull=True).__getstate__() ],
        }
        if self.decimal_places == 0:
            data["map"].extend([ r.__getstate__() for r in self.pointcolourrange_set.filter(min_value_int__isnull=False)])
        else:
            data["map"].extend([ r.__getstate__() for r in self.pointcolourrange_set.filter(min_value_dec__isnull=False)])
        return data
    def validate(self):
        problems = []
        ranges = self.pointcolourrange_set.all()
        if ranges.count() == 0:
            problems.append("Point colour map %s has no ranges defined" % self.label)
        elif ranges.count() == 1:
            problems.append("Point colour map %s has only one range defined - map redundant" % self.label)
        gotnull = 0
        for r in ranges:
            if r.min_value() is None:
                gotnull += 1
        if gotnull != 1:
            problems.append("Colour map %s has no null minimum value range")
        return problems

class PointColourRange(models.Model):
    colour_map = models.ForeignKey(PointColourMap)
    min_value_dec = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    min_value_int = models.IntegerField(blank=True, null=True)
    colour = models.CharField(max_length=50)
    class Meta:
        ordering = ('colour_map', 'min_value_dec', 'min_value_int')
        unique_together = (('colour_map', 'min_value_dec', 'min_value_int'),)
    def __unicode__(self):
        return "%s-%s" % (self.colour_map.label, self.colour)
    def min_value(self):
        if self.colour_map.decimal_places == 0:
            return self.min_value_int
        else:
            if self.min_value_dec is None:
                return self.min_value_dec.quantize(Decimal(10)**(-1 * self.colour_map.decimal_places), ROUND_HALF_UP)
            else:
                return None
    def min_value_json(self):
        minval = self.min_value()
        if isinstance(minval, Decimal):
            return float(minval)
        else:
            return minval
    def export(self):
        return { "colour": self.colour, "min_value": self.min_value_json() }
    def __getstate__(self):
        return self.export()
    @classmethod
    def import_data(cls, pcm, data):
        pcr = PointColourRange(colour_map=pcm, colour=data["colour"])
        if pcm.decimal_places == 0:
            pcr.min_value_int = data["min_value"]
        elif data["min_value"]:
            pcr.min_value_dec = Decimal(data["min_value"]).quantize(Decimal(10)**(-1*self.colour_map.decimal_places), rounding=decimal.ROUND_HALF_UP)
        pcr.save()
        return pcr

class GraphDisplayOptions(models.Model):
    LINE_NONE = 0
    LINE_STRAIGHT = 1
    LINE_BEZIER = 2
    line_options = [ "none", "straight", "bezier" ]
    line_option_choices = [
            (LINE_NONE, line_options[LINE_NONE]),
            (LINE_STRAIGHT, line_options[LINE_STRAIGHT]),
            (LINE_BEZIER, line_options[LINE_BEZIER]),
    ]
    POINT_NONE = 0
    POINT_CIRCLE = 1
    POINT_SQUARE = 2
    POINT_TRIANGLE = 3
    POINT_VERTICAL_BARS = 4
    point_options = [ "none", "circle", "square", "triangle", "vertical-bars" ]
    point_option_choices = [
            (POINT_NONE, point_options[POINT_NONE]),
            (POINT_CIRCLE, point_options[POINT_CIRCLE]),
            (POINT_SQUARE, point_options[POINT_SQUARE]),
            (POINT_TRIANGLE, point_options[POINT_TRIANGLE]),
            (POINT_VERTICAL_BARS, point_options[POINT_VERTICAL_BARS]),
    ]
    lines = models.SmallIntegerField(choices=line_option_choices, default=LINE_NONE)
    points = models.SmallIntegerField(choices=point_option_choices, default=POINT_NONE)
    single_graph = models.BooleanField(default=True)
    rotates = models.BooleanField(default=False)
    shaded = models.BooleanField(default=False)
    stacked = models.BooleanField(default=False)
    point_colour_map = models.ForeignKey(PointColourMap, blank=True, null=True)
    graph=models.OneToOneField(GraphDefinition)
    @classmethod
    def create_default(cls, g):
        try:
            do = g.graphdisplayoptions
        except GraphDisplayOptions.DoesNotExist:
            do = GraphDisplayOptions(graph=g)
        if g.graph_type == g.LINE:
            do.lines = cls.LINE_STRAIGHT
        else:
            do.lines = cls.LINE_NONE
        do.shaded = False
        do.points = cls.POINT_NONE
        do.single_graph = True
        do.stacked = False
        do.point_colour_map = None
        do.save()
        return do
    @classmethod
    def import_data(cls, g, data):
        try:
            do = g.graphdisplayoptions
        except GraphDisplayOptions.DoesNotExist:
            do = GraphDisplayOptions(graph=g)
        do.lines = data["lines"]
        do.points = data["points"]
        do.stacked = data["stacked"]
        do.shaded = data["shaded"]
        do.single_graph = data["single_graph"]
        do.rotates = data.get("single_graph", False)
        if data["point_colour_map"]:
            do.point_colour_map = PointColourMap.objects.get(label=data["point_colour_map"])
        else:
            do.point_colour_map = None
        do.save()
        return do
    def export(self):
        data = {
            "lines": self.lines,    
            "points": self.points,    
            "single_graph": self.single_graph,    
            "rotates": self.rotates,    
            "stacked": self.stacked,    
            "shaded": self.shaded,    
        }
        if self.point_colour_map:
            data["point_colour_map"] = self.point_colour_map.label
        else:
            data["point_colour_map"] = None
        return data
    def __getstate__(self, graph_type):
        if graph_type == GraphDefinition.LINE:
            data = {
                "lines": self.line_options[self.lines],
                "points": self.point_options[self.points],
                "single_graph": self.single_graph,
                "shaded": self.shaded,
            }
            if not self.single_graph:
                data["rotates"] = self.rotates
            if self.points:
                if self.point_colour_map:
                    data["point_colour_map"] = self.point_colour_map.__getstate__()
                else:
                    data["point_colour_map"] = None
        elif graph_type in (GraphDefinition.HISTOGRAM, GraphDefinition.BAR):
            data = {
                "stacked": self.stacked,
                "single_graph": self.single_graph,
            }
            if not self.single_graph:
                data["rotates"] = self.rotates
        else:
            data = {}
        return data
    def clean(self):
        if self.graph.graph_type == GraphDefinition.LINE:
            self.stacked = False
            if self.points == self.POINT_NONE:
                self.point_colour_map = None
            if self.single_graph:
                self.rotates = False
        elif self.graph.graph_type in (GraphDefinition.HISTOGRAM, GraphDefinition.BAR):
            self.lines = self.LINE_NONE
            self.points = self.POINT_NONE
            self.shaded = False
            self.point_colour_map = None
            if self.single_graph:
                self.rotates = False
        else:
            self.lines = self.LINE_NONE
            self.points = self.POINT_NONE
            self.shaded = False
            self.stacked = False
            self.single_graph = True
            self.rotates = False
            self.point_colour_map = None
        self.save()
    def validate(self):
        problems = []
        self.clean()
        if self.graph.graph_type == GraphDefinition.LINE:
            if self.lines == self.LINE_NONE and self.points == self.POINT_NONE:
                problems.append("Graph for tile %s of widget %s is a line graph but displays neither lines nor datapoints" % (self.graph.tile.url, self.graph.widget.url()))
            if self.shaded and self.lines == self.LINE_NONE:
                problems.append("Graph for tile %s of widget %s is shaded but does not display a line to shade under" % (self.graph.tile.url, self.graph.widget.url()))
            if self.point_colour_map:
                problems.extend(self.point_colour_map.validate())
        return problems

class GraphClusterBase(models.Model):
    # Histo/bar clusters or Pies
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField(verbose_name="label")
    label=models.CharField(verbose_name="name", max_length=80)
    hyperlink=models.URLField(blank=True, null=True)
    sort_order=models.IntegerField()
    def __unicode__(self):
        return self.url
    class Meta:
        abstract=True
        unique_together = [("graph", "sort_order"), ("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "sort_order" ]
    def __getstate__(self, view=None):
        return {
            "label": self.url,
            "name": parametise_label(self.graph.tile.widget, view, self.label),
            "hyperlink": parametise_label(self.graph.tile.widget, view, self.hyperlink),
        }

class GraphCluster(GraphClusterBase):
    def export(self):
        return {
            "url": self.url,
            "sort_order": self.sort_order,
            "label": self.label,
            "hyperlink": self.hyperlink,
        }
    @classmethod
    def import_data(cls, g, data):
        try:
            c = GraphCluster.objects.get(graph=g, url=data["url"])
        except GraphCluster.DoesNotExist:
            c = GraphCluster(graph=g, url=data["url"])
        c.sort_order = data["sort_order"]
        c.label = data["label"]
        c.hyperlink = data["hyperlink"]
        c.save()

class GraphDataset(models.Model):
    # Lines, Bars, or Sectors
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField(verbose_name="label")
    label=models.CharField(verbose_name="name", max_length=80)
    dynamic_label=models.BooleanField(default=False)
    colour = models.CharField(max_length=50)
    use_secondary_numeric_axis = models.BooleanField(default=False)
    use_error_bars = models.BooleanField(default=False)
    hyperlink=models.URLField(blank=True, null=True)
    sort_order=models.IntegerField()
    class Meta:
        unique_together = [("graph", "url"), ("graph", "sort_order"), ("graph", "label")]
        ordering = [ "graph", "sort_order" ]
    def clean(self):
        if not self.graph.use_secondary_numeric_axis:
            self.use_secondary_numeric_axis = False
    def export(self):
        return {
            "url": self.url,
            "sort_order": self.sort_order,
            "label": self.label,
            "dynamic_label": self.dynamic_label,
            "colour": self.colour,
            "hyperlink": self.hyperlink,
            "use_secondary_numeric_axis": self.use_secondary_numeric_axis,
            "use_error_bars": self.use_error_bars,
        }
    def __unicode__(self):
        return self.url
    @classmethod
    def import_data(cls, g, data):
        try:
            d = GraphDataset.objects.get(graph=g, url=data["url"])
        except GraphDataset.DoesNotExist:
            d = GraphDataset(graph=g, url=data["url"])
        d.label = data["label"]
        d.sort_order = data["sort_order"]
        d.colour = data["colour"]
        d.hyperlink = data["hyperlink"]
        d.use_secondary_numeric_axis = data["use_secondary_numeric_axis"]
        d.use_error_bars = data.get("use_error_bars", False)
        d.dynamic_label = data.get("dynamic_label", False)
        d.save()
    def __getstate__(self, view=None):
        state = {
            "label": self.url,
            "name": parametise_label(self.graph.tile.widget, view, self.label),
            "colour": self.colour,
            "hyperlink": parametise_label(self.graph.tile.widget, view, self.hyperlink),
            "dynamic_name_display": self.dynamic_label,
        }
        if self.graph.use_secondary_numeric_axis:
            if self.graph.graph_type == self.graph.LINE:
                state["use_secondary_vertical_axis"] = self.use_secondary_numeric_axis
            else:
                state["use_secondary_numeric_axis"] = self.use_secondary_numeric_axis
            state["use_error_bars"] = self.use_error_bars
        return state

