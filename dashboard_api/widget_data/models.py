from decimal import Decimal, ROUND_HALF_UP
import datetime
import pytz

from django.conf import settings
from django.db import models

# Create your models here.
tz = pytz.timezone(settings.TIME_ZONE)

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
                if self.decval is None:
                    return None
                else:
                    return unicode(self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP))
        else:
            return self.strval
    def value(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return self.intval
            else:
                if self.decval is None:
                    return None
                else:
                    return self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP)
        else:
            return self.strval
    def __unicode__(self):
        return "<Data for %s>" % unicode(self.statistic)

class StatisticListItem(models.Model):
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    MONTH = 5
    QUARTER = 6
    YEAR = 7
    levels = [ "N/A", "second", "minute", "hour",
               "day", "month", "quarter", "year" ]
    level_choices = [
        ( SECOND, "second" ),
        ( MINUTE, "minute" ),
        ( HOUR, "hour" ),
        ( DAY, "day" ),
        ( MONTH, "month" ),
        ( QUARTER, "quarter" ),
        ( YEAR, "year" ),
    ]
    statistic = models.ForeignKey("widget_def.Statistic")
    keyval = models.CharField(max_length=120, null=True, blank=True)
    datetime_key = models.DateTimeField(null=True, blank=True)
    datetime_keylevel = models.SmallIntegerField(choices=level_choices, 
                        null=True, blank=True)
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
    def set_datetime_key(self, key, level=None):
        if self.statistic.use_datekey():
            self.datetime_key = tz.localize(datetime.datetime.combine(key, datetime.time()))
        elif self.statistic.use_datetimekey():
            if level is None or level == self.SECOND:
                self.datetime_key = key
            elif level == self.MINUTE:
                key = key.replace(second=0)
                self.datetime_key = key
            elif level == self.HOUR:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                self.datetime_key = key
            elif level == self.DAY:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                self.datetime_key = key
            elif level == self.MONTH:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                self.datetime_key = key
            elif level == self.QUARTER:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                key = key.replace(month=((key.month - 1) / 3) * 3 + 1)
                self.datetime_key = key
            elif level == self.YEAR:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                key = key.replace(month=1)
                self.datetime_key = key
            else:
                raise Exception("set_datetime_key: Invalid level passed: %s" % repr(level))
            self.datetime_keylevel=level
        else:
            raise Exception("set_datetime_key called on non date(time) key statistic: %s" % repr(level))
    def display_datetime_key(self):
        if self.statistic.use_datekey():
            return self.datetime_key.strftime("%Y-%m-%d")
        elif self.statistic.use_datetimekey():
            if self.datetime_keylevel in (None, self.SECOND, self.MINUTE, self.HOUR):
                return self.datetime_key.astimezone(tz).strftime("%Y-%m-%dT%H:%M:%S")
            elif self.datetime_keylevel in (self.DAY, self.MONTH):
                return self.datetime_key.astimezone(tz).strftime("%Y-%m-%d")
            elif self.datetime_keylevel == self.QUARTER:
                qtr = (self.datetime_key.astimezone(tz).month - 1)/3 + 1
                return "%dQ%d" % (self.datetime_key.astimezone(tz).year, qtr)
            else: # self.datetime_keylevel == self.YEAR:
                return self.datetime_key.astimezone(tz).strftime("%Y")
        else:
            return None
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
        unique_together = ("statistic", "datetime_key", "datetime_keylevel", "sort_order")
        ordering = ("statistic", "datetime_key", "-datetime_keylevel", "sort_order")

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
        elif graph.horiz_axis_type == graph.DATETIME:
            args.append("horiz_dateval")
            args.append("horiz_timeval")
        if graph.use_numeric_axes:
            args.append("value")
        return self.order_by(*args)
    natural_order.queryset_only = True

class GraphData(models.Model):
    graph = models.ForeignKey("widget_def.GraphDefinition")
    cluster = models.ForeignKey("widget_def.GraphCluster", blank=True, null=True)
    dataset = models.ForeignKey("widget_def.GraphDataset", blank=True, null=True)
    value = models.DecimalField(max_digits=14, decimal_places=4,
                        blank=True, null=True)
    horiz_numericval = models.DecimalField(max_digits=14, decimal_places=4,
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
        elif self.graph.horiz_axis_type == self.graph.DATETIME:
            return tz.localize(datetime.datetime.combine(self.horiz_dateval,self.horiz_timeval))
        else:
            return None
    def horiz_json_value(self):
        return self.graph.jsonise_horiz_value(self.horiz_value())
    class Meta:
        ordering = ("graph", "cluster", "dataset", "horiz_numericval", "horiz_dateval", "horiz_timeval")

class RawDataRecord(models.Model):
    rds = models.ForeignKey("widget_def.RawDataSet")
    sort_order = models.IntegerField()
    csv = models.TextField(null=True)
    def update_csv(self):
        out = ""
        first_cell = True
        for col in self.rds.rawdatasetcolumn_set.all():
            if not first_cell:
                out += ","
            try:
                rd = self.rawdata_set.get(column=col)
                out += rd.csv()
            except RawData.DoesNotExist:
                pass
            first_cell = False
        out += "\n"
        self.csv = out
        self.save()
    def json(self):
        result = {}
        for col in self.rds.rawdatasetcolumn_set.all():
            try:
                rd = self.rawdata_set.get(column=col)
                result[col.url] = rd.json_val()
            except RawData.DoesNotExist:
                result[col.url] = None
        return result
    class Meta:
        unique_together=("rds", "sort_order")
        ordering = ("rds", "sort_order")

class RawData(models.Model):
    record = models.ForeignKey(RawDataRecord)
    column = models.ForeignKey("widget_def.RawDataSetColumn")
    value = models.CharField(max_length=1024, blank=True)
    def csv(self):
        out = self.value.replace('"', '""')
        if '"' in out or ',' in out:
            return '"%s"' % out
        else:
            return out
    def json_val(self):
        try:
            return int(self.value)
        except Exception, e:
            pass
        try:
            return float(self.value)
        except Exception, e:
            pass
        return self.value
    class Meta:
        unique_together=("record", "column")
        ordering = ("record", "column")

