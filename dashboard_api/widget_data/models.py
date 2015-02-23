from decimal import Decimal, ROUND_HALF_UP
import datetime
import pytz

from django.conf import settings
from django.db import models

# Create your models here.

def update_widget(widget_def):
    widget_def.last_updated = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    widget_def.save()

class StatisticData(models.Model):
    statistic = models.ForeignKey("widget_def.Statistic", unique=True)
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
    def save(self, *args, **kwargs):
        update_widget(self.statistic.tile.widget)
        super(StatisticData, self).save(*args, **kwargs)
    def __unicode__(self):
        return "<Data for %s>" % unicode(self.statistic)

class StatisticListItem(models.Model):
    statistic = models.ForeignKey("widget_def.Statistic")
    keyval = models.CharField(max_length=120, null=True, blank=True)
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
    sort_order = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        update_widget(self.statistic.tile.widget)
        super(StatisticData, self).save(*args, **kwargs)
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
        unique_together = ("statistic", "sort_order")
        ordering = ("statistic", "sort_order")

