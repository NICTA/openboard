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

from decimal import Decimal

from django.db import models

from widget_data.models import GraphData, GraphDatasetData
from widget_def.models.graphbase import GraphClusterBase
from widget_def.models.tile_def import TileDefinition
from widget_def.parametisation import parametise_label, resolve_pval

# Create your models here.

class GraphDefinition(models.Model):
    """
    Defines a graph object (within a graph tile, within a widget).

    Supported types:

    line: 
        A graph where both the horizontal and vertical axes represent continuous quantifiable 
        variables (e.g. numeric, date, time).  Multiple datasets (e.g. as represented by 
        different coloured dots/lines) may be presented in the one graph, against up to two 
        independent vertical axes.

        There is an implicit assumption that each dataset's vertical axis values represent 
        some (arbitrary) function of the dataset's horizontal axis value.
        
        The canonical version would be line graph with a set of continuous lines interpolating 
        data between discretely sampled data-points, but other visualisations are possible.

    histogram:
        A graph where the vertical axis represents a continuous numeric variable, and the 
        horizontal axis represents a discrete variable, or a cartesion product of two discrete
        variables.

        The canonical version would be a clustered histogram.  The clusters of bars are represented
        by GraphCusters and the bars within each cluster by GraphDatasets.  Bars may be plotted against
        up to two independent vertical/numeric axes.

    bar:
        As for a histogram, except rotated - the horizontal axis representing a continuous numeric 
        variable and the vertical axis represents a discrete variable, or a cartesion product of 
        two discrete variables. 

    pie:
        A chart displaying the relative proportions of discrete set of options.

        The canonical version would be a pie chart, or more generally a collection of pie charts.

        The segments in the pie(s) are represented by GraphDatasets and each pie is represented by
        a GraphCluster.

        Note that is only the proportion of the total for each cluster that is represented in a pie
        chart.  e.g. 20:10:10 will appear exactly the same as 2:1:1.  Many loaders will no doubt find
        it simplest to normalise values to add to 100 (i.e. 50:25:25), however this is not required.
    """
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
                                        tile_type__in=(TileDefinition.GRAPH, TileDefinition.GRAPH_SINGLE_STAT),
                                ), 
                    help_text="The widget tile this graph is to be displayed in")
    heading = models.CharField(max_length=120, blank=True, null=True, help_text="The heading for the graph, as displayed to the end-user.")
    graph_type = models.SmallIntegerField(choices=(
                    (LINE, graph_types[LINE]),
                    (HISTOGRAM, graph_types[HISTOGRAM]),
                    (BAR, graph_types[BAR]),
                    (PIE, graph_types[PIE]),
                ), help_text="The type of graph")
    numeric_axis_label = models.CharField(max_length=120, verbose_name="Numeric axis name", blank=True, null=True, help_text="A descriptive name for the (main) numeric axis, suitable for displaying to the end-user (as an axis label).  For line, bar and histogram type graphs.  For line-graphs the 'numeric axis' is the vertical axis, even if the horizontal axis is numeric as well.")
    numeric_axis_always_show_zero = models.BooleanField(default=True, help_text="If true, the main numeric axis zero point should always be displayed on the graph. If false, the zero point may be hidden to focus on the actual value range the data covers. If the data crosses the zero point, then the zero point will be displayed either way. For line, bar and histogram graphs.")
    use_secondary_numeric_axis = models.BooleanField(default=False, help_text="If true, there is an independent secondary numeric axis against which datasets can be plotted. For line, bar and histogram graphs.")
    secondary_numeric_axis_label = models.CharField(max_length=120, verbose_name="Secondary numeric axis name", blank=True, null=True, help_text="A descriptive name for the secondary numeric axis, suitable for displaying to the end-user (as an axis label).  For line, bar and histogram type graphs that use a secondary numeric axis.")
    secondary_numeric_axis_always_show_zero = models.BooleanField(default=True, help_text="If true, the secondary numeric axis zero point should always be displayed on the graph. If false, the zero point may be hidden to focus on the actual value range the data covers. If the data crosses the zero point, then the zero point will be displayed either way. For line, bar and histogram graphs that use a secondary numeric axis.")
    cluster_label = models.CharField(max_length=120, default="cluster", help_text="An overall heading for clusters.  E.g. if each cluster represents a city, then the cluster_label might be 'City' or 'Cities'. Not used for line graphs.")
    dataset_label = models.CharField(max_length=120, default="dataset", help_text="An overall heading for datasets.  E.g. if each dataset represents a city, then the dataset_label might be 'City' or 'Cities'. Not used for line graphs.")
    dynamic_clusters = models.BooleanField(default=False, help_text="If true, clusters are not defined statically, but created at load time and provided to clients as part of the widget data.")
    horiz_axis_label = models.CharField(max_length=120, blank=True, null=True, help_text="The label for the horizontal axis. For line graphs only.")
    horiz_axis_type = models.SmallIntegerField(choices=(
                    (0, axis_types[0]),
                    (NUMERIC, axis_types[NUMERIC]),
                    (DATE, axis_types[DATE]),
                    (TIME, axis_types[TIME]),
                    (DATETIME, axis_types[DATETIME]),
                ), default=0, help_text="The data-type for the horizontal axis. For line graphs only.")
    def widget(self):
        """Returns the widget this graph ultimately belongs to."""
        return self.tile.widget
    def numeric_axis_name(self):
        """
        Whether the data API should call the numeric_axis "numeric_axis" (histogram, bar, pie charts) or "vertical_axis" (line graphs).
        """
        if self.graph_type == self.LINE:
            return "vertical_axis"
        else:
            return "numeric_axis"
    def clusters(self, pval=None):
        """
        Returns the (static or dynamic as appropriate) clusters for this graph.
        """
        if self.dynamic_clusters:
            return self.dynamicgraphcluster_set.filter(param_value=pval)
        else:
            return self.graphcluster_set.all()
    def is_histogram(self):
        """Returns True for bar and histogram graphs. False otherwise."""
        return self.graph_type in (self.BAR, self.HISTOGRAM)
    def use_numeric_axes(self):
        """Returns true if there the graph has a true numeric axis. i.e. everything except pie charts"""
        return self.graph_type in (self.LINE, self.HISTOGRAM, self.BAR)
    def use_clusters(self):
        """Returns true if graph is of a type that can use clusters. i.e. everything except line graphs"""
        return self.graph_type in (self.PIE, self.HISTOGRAM, self.BAR)
    def initial_form_data(self, pval=None, view=None):
        """Return the current graphdata in a form ready to pass to a the graph formset as initial data."""
        return [ self.initial_form_datum(gd) for gd in self.get_data(view=view,pval=pval) ]
    def initial_form_datum(self, gd):
        """Covert a :model:`widget_data.GraphData` object into a form suitable for a graph data dynamic form."""
        result = {}
        result["value"] = gd.value
        result["dataset"] = gd.dataset
        if self.use_clusters(): 
            result["cluster"] = gd.get_cluster()
        else:
            result["horiz_value"] = gd.horiz_value()
        if gd.dataset.use_error_bars:
            result["err_valmin"] = gd.err_valmin
            result["err_valmax"] = gd.err_valmax
        return result
    def initial_override_form_data(self, pval=None):
        """Initial data for the supplementary graph data forms. (Dynamic dataset labels and dynamic clusters.)"""
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
        """Get the data for this graph (parametised if necessary)"""
        pval = resolve_pval(self.widget().parametisation, view=view, pval=pval)
        return GraphData.objects.filter(graph=self,param_value=pval).natural_order(self)
    def get_last_datum(self, dataset, cluster=None, pval=None):
        """Return the last (as per natural graph data sort order) data item for a gvien graph slice (dataset/cluster)"""
        return GraphData.objects.filter(graph=self, 
                            dataset__url=dataset, 
                            param_value=pval,
                            cluster__url=cluster).natural_order(self).last()
    def data_last_updated(self, update=False, view=None, pval=None):
        """
        Return when the data for this graph was last updated (with parametisation if necessary).

        update: If true and the last_updated value is cached, then the cached value is dropped and recalculated.
        """
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
        """Take a horizontal axis value for this graph and convert to an appropriate json format."""
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
            state["sector_label"] = self.dataset_label
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
            if not self.cluster_label:
                self.cluster_label = "cluster"
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
    """
    Represents a colour map that allows different points on a line graph to be colour coded by their value.
    """
    label=models.CharField(verbose_name="name", max_length=50, unique=True, help_text="A label to identify this colour map to support re-use.")
    decimal_places = models.SmallIntegerField(default=0, help_text="Numeric precision of data-range values for this map. Good for it to match the numeric_axis type of the graph, but not required.")
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
    """
    Represents the data range for a single colour within a :model:`widget_def.PointColourMap`

    Each colour range has a minimum value - if the point value is greater than the minimum value and less than the 
    minimum value of next PointColourRange, then this colour is used.  The first colour range in a map may have a 
    null minimum value.
    """
    colour_map = models.ForeignKey(PointColourMap, help_text="The PointColourMap object")
    min_value_dec = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, help_text="The minimum value for this colour range, used if PointColourMap.decimal_places != 0.")
    min_value_int = models.IntegerField(blank=True, null=True)
    colour = models.CharField(max_length=50, help_text="The colour. Format is implementation specific. May be e.g. a hex code, or may simply be a word colour-hint.")
    class Meta:
        ordering = ('colour_map', 'min_value_dec', 'min_value_int')
        unique_together = (('colour_map', 'min_value_dec', 'min_value_int'),)
    def __unicode__(self):
        return "%s-%s" % (self.colour_map.label, self.colour)
    def min_value(self):
        """Return this range's minimum value, as interpreted through the map's decimal_places."""
        if self.colour_map.decimal_places == 0:
            return self.min_value_int
        else:
            if self.min_value_dec is None:
                return self.min_value_dec.quantize(Decimal(10)**(-1 * self.colour_map.decimal_places), ROUND_HALF_UP)
            else:
                return None
    def min_value_json(self):
        """Return this range's minimum value as a json-ready value, as interpreted through the map's decimal_places."""
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
    """
    Graph display options.
   
    Graph options that are purely cosmetic and contain no structural meta-data.

    Line options (for line graphs only):
       none: No lines joining points - points only.
       straight: Straight lines join points.
       bezier: Bezier (or similar) curves join points.

    Point options (for line graphs only):
       none: No points, show lines only.
       circle: Represent datapoints as small circles.
       square: Represent datapoints as small squares.
       triangle: Represent datapoints as small triangles.
       vertical-bars: Represent datapoints as vertical bars extending to the horizontal axis.
                Produces line-graphs that look like histograms.
    """
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
    lines = models.SmallIntegerField(choices=line_option_choices, default=LINE_NONE, help_text="For line graphs, how to display the lines between datapoints.")
    points = models.SmallIntegerField(choices=point_option_choices, default=POINT_NONE, help_text="For line graphs, how to display the datapoints.")
    single_graph = models.BooleanField(default=True, help_text="If false a line graph with multiple datasets is to be displayed as a set of single dataset graphs and a bar chart or histogram is displayed as a set of separate histograms instead of a single clustered histogram. Not supported for pie charts.")
    rotates = models.BooleanField(default=False, help_text="Can only be true if single graph is false.  Rather than a set of graphs being displayed, a single graph is at a time, but the various graphs are gradually rotated through. Not supported for pie charts.")
    shaded = models.BooleanField(default=False, help_text="For line graphs only. If true, the area under the line is to be shaded. Cannot be set if lines=none.")
    stacked = models.BooleanField(default=False, help_text="For bar or histogram charts only. If true they are displayed as a stacked histogram instead of a clustered histogram.  (i.e. the bars for each cluster are stacked on top of each other instead of being placed side by side)")
    point_colour_map = models.ForeignKey(PointColourMap, blank=True, null=True, help_text="""Indicates how points should be coloured, based on their vertical axis value.  Optional.  If null, then use the colours in the Graph Dataset Definition.  N.B. Must be null if "points" is "none".""")
    graph=models.OneToOneField(GraphDefinition, help_text="The graph")
    @classmethod
    def create_default(cls, g):
        """Create a default GraphDisplayOption object for a new graph."""
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
        do.rotates = data.get("rotates", False)
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
    """
        Abstract base model for graph clusters.  Parent of both the static and dynamic graph cluster models.

        Graph clusters represent clusters in clustered histograms or bar charts, and separate pies in a pie chart. 
        They are not used by line graphs.
    """
    # Histo/bar clusters or Pies
    graph=models.ForeignKey(GraphDefinition, help_text="The graph this cluster belongs to.")
    url=models.SlugField(verbose_name="label", help_text="A short symbolic label for the cluster, as used in the API.")
    label=models.CharField(verbose_name="name", max_length=80, help_text="A longer human-readable description of the cluster.")
    hyperlink=models.URLField(blank=True, null=True, help_text="An optional external URL for this cluster to link to.")
    sort_order=models.IntegerField(help_text="How to sort this cluster within the graph.")
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
    """Represents a statically defined graph cluster."""
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
    """
    Represents a graph dataset

    A graph dataset represents a line in a line graph, a bar (within a cluster) for a bar chart or histogram, or a sector in pie chart.

    A simple way to tell the difference between a cluster and dataset is that a dataset is colour-coded.
    """
    # Lines, Bars, or Sectors
    graph=models.ForeignKey(GraphDefinition, help_text="The graph the dataset belongs to")
    url=models.SlugField(verbose_name="label", help_text="A short symbolic label for the dataset, as used in the API.")
    label=models.CharField(verbose_name="name", max_length=80, help_text="A longer human-readable description of the dataset.")
    dynamic_label=models.BooleanField(default=False, help_text="If false, the name (label) of the dataset is used. If true, this may be over-ridden by a dynamic value supplied with the data for the graph.")
    colour = models.CharField(max_length=50, help_text="The colour of the dataset. Interpretation is implementation-specific. Typically a word colour hint rather than an explicit rgb value.")
    use_secondary_numeric_axis = models.BooleanField(default=False, help_text="If true, data for this dataset are plotted against the graph's secondary numeric axis (which obviously must be defined). Not supported for pie charts.")
    use_error_bars = models.BooleanField(default=False, help_text="If true the data for this dataset will be accompanied by an upper and lower uncertainty limit, which may be plotted as error-bars. Not supported for pie charts.")
    hyperlink=models.URLField(blank=True, null=True, help_text="An optional external URL for this dataset to link to.")
    sort_order=models.IntegerField(help_text="How to sort this dataset within the graph.")
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

