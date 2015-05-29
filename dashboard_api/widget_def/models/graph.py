from django.db import models

from widget_data.models import GraphData
from widget_def.models.tile_def import TileDefinition

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
        axis_types = [ "-", "numeric", "date", "time" ]
        tile = models.OneToOneField(TileDefinition, limit_choices_to={
                                'tile_type': TileDefinition.GRAPH
                                })
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
        stacked=models.BooleanField(default=False)
        def widget(self):
            return self.tile.widget
        def numeric_axis_name(self):
            if self.graph_type == self.LINE:
                return "vertical_axis"
            else:
                return "numeric_axis"
        def is_histogram(self):
            return self.graph_type in (self.BAR, self.HISTOGRAM)
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
                "stacked": self.stacked,
                "clusters": { c.url: c.export() for c in self.graphcluster_set.all() },
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
            g.stacked = data.get("stacked", False)
            g.horiz_axis_label = data["horiz_axis_label"]
            g.horiz_axis_type = data["horiz_axis_type"]
            g.save()
            cluster_urls = []
            for (c_url, c_data) in data["clusters"].items():
                GraphCluster.import_data(g, c_url, c_data)
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
                "url": self.tile.url,
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
                state["clusters"] = { c.url: c.__getstate__() for c in self.graphcluster_set.all() }
                state["bars"] = { d.url: d.__getstate__() for d in self.graphdataset_set.all()}
                state["stacked"] = self.stacked
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
            if self.stacked and not self.is_histogram():
                problems.append("Only Histogram or Bar graphs can be stacked")
            return problems

class GraphCluster(models.Model):
    # Histo/bar clusters or Pies
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField()
    label=models.CharField(max_length=80)
    hyperlink=models.URLField(blank=True, null=True)
    def __unicode__(self):
        return self.url
    class Meta:
        unique_together = [("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "url" ]
    def export(self):
        return {
            "label": self.label,
            "hyperlink": self.hyperlink,
        }
    def __getstate__(self):
        return {
            "label": self.label,
            "hyperlink": self.hyperlink,
        }
    @classmethod
    def import_data(cls, g, url, data):
        try:
            c = GraphCluster.objects.get(graph=g, url=url)
        except GraphCluster.DoesNotExist:
            c = GraphCluster(graph=g, url=url)
        c.label = data["label"]
        c.hyperlink = data["hyperlink"]
        c.save()

class GraphDataset(models.Model):
    # Lines, Bars, or Sectors
    graph=models.ForeignKey(GraphDefinition)
    url=models.SlugField()
    label=models.CharField(max_length=80)
    colour = models.CharField(max_length=50)
    use_secondary_numeric_axis = models.BooleanField(default=False)
    hyperlink=models.URLField(blank=True, null=True)
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
            "hyperlink": self.hyperlink,
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
        d.hyperlink = data["hyperlink"]
        d.use_secondary_numeric_axis = data["use_secondary_numeric_axis"]
        d.save()
    def __getstate__(self):
        state = {
            "label": self.label,
            "colour": self.colour,
            "hyperlink": self.hyperlink,
        }
        if self.graph.use_secondary_numeric_axis:
            if self.graph.graph_type == self.graph.LINE:
                state["use_secondary_vertical_axis"] = self.use_secondary_numeric_axis
            else:
                state["use_secondary_numeric_axis"] = self.use_secondary_numeric_axis
        return state

