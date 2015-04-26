from decimal import Decimal, ROUND_HALF_UP
import datetime
import pytz

from django.conf import settings
from django.db import models

# Create your models here.

class WidgetData(models.Model):
    widget = models.OneToOneField("widget_def.WidgetDefinition")
    actual_frequency_text = models.CharField(max_length=60, blank=True, null=True)

class StatisticData(models.Model):
    statistic = models.OneToOneField("widget_def.Statistic")
    label=models.CharField(max_length=80, blank=True, null=True)
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    traffic_light_code = models.ForeignKey("widget_def.TrafficLightScaleCode", blank=True, null=True)
    icon_code = models.ForeignKey("widget_def.IconCode", blank=True, null=True)
    trend = models.SmallIntegerField(choices=(
                    (1, "Upwards"),
                    (0, "Steady"),
                    (-1, "Downwards"),
                ), blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    def display_val(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return unicode(self.intval)
            else:
                return unicode(self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP))
        else:
            return self.strval
    def value(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return self.intval
            else:
                return self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP)
        else:
            return self.strval
    def __unicode__(self):
        return "<Data for %s>" % unicode(self.statistic)

class StatisticListItem(models.Model):
    statistic = models.ForeignKey("widget_def.Statistic")
    keyval = models.CharField(max_length=120, null=True, blank=True)
    datekey = models.DateField(null=True, blank=True)
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    traffic_light_code = models.ForeignKey("widget_def.TrafficLightScaleCode", blank=True, null=True)
    icon_code = models.ForeignKey("widget_def.IconCode", blank=True, null=True)
    trend = models.SmallIntegerField(choices=(
                    (1, "Upwards"),
                    (0, "Steady"),
                    (-1, "Downwards"),
                ), blank=True, null=True)
    sort_order = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    def display_val(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return unicode(self.intval)
            else:
                return unicode(self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP))
        else:
            return self.strval
    def value(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return self.intval
            else:
                return self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP)
        else:
            return self.strval
    def __unicode__(self):
        return "<List for %s (%d)>" % (unicode(self.statistic), self.sort_order)
    class Meta:
        unique_together = ("statistic", "datekey", "sort_order")
        ordering = ("statistic", "datekey", "sort_order")

class GraphDataQuerySet(models.QuerySet):
    def natural_order(self, graph):
        # args = ["graph", "cluster", "dataset"]
        args = ["graph", ]
        if graph.use_clusters():
            args.append("cluster")
        args.append("dataset")
        if graph.horiz_axis_type == graph.NUMERIC:
            args.append("horiz_numericval")
        elif graph.horiz_axis_type == graph.DATE:
            args.append("horiz_dateval")
        elif graph.horiz_axis_type == graph.TIME:
            args.append("horiz_timeval")
        if graph.use_numeric_axes:
            args.append("value")
        return self.order_by(*args)
    natural_order.queryset_only = True

class GraphData(models.Model):
    graph = models.ForeignKey("widget_def.GraphDefinition")
    cluster = models.ForeignKey("widget_def.GraphCluster", blank=True, null=True)
    dataset = models.ForeignKey("widget_def.GraphDataset", blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    horiz_numericval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    horiz_dateval = models.DateField(blank=True, null=True)
    horiz_timeval = models.TimeField(blank=True, null=True)
    objects = GraphDataQuerySet.as_manager()
    last_updated = models.DateTimeField(auto_now=True)
    def horiz_value(self):
        if self.graph.horiz_axis_type == self.graph.NUMERIC:
            return self.horiz_numericval
        elif self.graph.horiz_axis_type == self.graph.DATE:
            return self.horiz_dateval
        elif self.graph.horiz_axis_type == self.graph.TIME:
            return self.horiz_timeval
        else:
            return None
    def horiz_json_value(self):
        return self.graph.jsonise_horiz_value(self.horiz_value())
    class Meta:
        ordering = ("graph", "cluster", "dataset")
