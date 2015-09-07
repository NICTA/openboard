import datetime
import decimal

from django.apps import apps
from django.contrib.gis.db import models

from widget_def.view_utils import csv_escape

class GeoFeature(models.Model):
    dataset = models.ForeignKey("widget_def.GeoDataset")
    geometry = models.GeometryField(null=True, blank=True)
    objects = models.GeoManager()
    last_updated = models.DateTimeField(auto_now=True)
    def csv(self):
        if self.dataset.geom_type == self.dataset.POINT:
            out = "%.12f,%.12f" % (self.geometry.y, self.geometry.x)
            skip_comma = False
        elif self.dataset.geom_type == self.dataset.PREDEFINED:
            out = ""
            skip_comma = True
        else:
            # Unsupported geometry type?
            out="ERROR"
            skip_comma = False
        for pd in self.dataset.geopropertydefinition_set.all():
            if skip_comma:
                skip_comma = False
            else:
                out += ","
            try:
                prop = self.geoproperty_set.get(prop=pd)
                out += csv_escape(prop.json_value())
            except GeoProperty.DoesNotExist:
                pass
        return out

class GeoProperty(models.Model):
    feature = models.ForeignKey(GeoFeature)
    prop = models.ForeignKey("widget_def.GeoPropertyDefinition")
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=15, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    dateval = models.DateField(null=True, blank=True)
    timeval = models.TimeField(null=True, blank=True)
    datetimeval = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    def heading(self, use_urls=True):
        if use_urls:
            return self.prop.url
        else:
            return self.prop.label
    def value(self):
        GeoPropertyDefinition = apps.get_app_config("widget_def").get_model("GeoPropertyDefinition")
        if self.prop.property_type == GeoPropertyDefinition.STRING:
            return self.strval
        elif self.prop.property_type == GeoPropertyDefinition.NUMERIC:
            if self.prop.num_precision == 0 and self.intval is not None:
                return self.intval
            else:
                return self.decval.quantize(decimal.Decimal(10)**(-1 * self.prop.num_precision), decimal.ROUND_HALF_UP)
        elif self.prop.property_type == GeoPropertyDefinition.DATE:
            return self.dateval
        elif self.prop.property_type == GeoPropertyDefinition.TIME:
            return self.timeval
        else:
            return self.datetimeval
    def json_value(self):
        GeoPropertyDefinition = apps.get_app_config("widget_def").get_model("GeoPropertyDefinition")
        if self.prop.property_type == GeoPropertyDefinition.DATE:
            return self.value().strftime("%Y-%m-%d")
        elif self.prop.property_type == GeoPropertyDefinition.TIME:
            return self.value().strftime("%H:%M:%S")
        elif self.prop.property_type == GeoPropertyDefinition.DATETIME:
            return self.value().strftime("%Y-%m-%dT%H:%M:%S")
        else:
            return unicode(self.value())
    def setval(self, value):
        GeoPropertyDefinition = apps.get_app_config("widget_def").get_model("GeoPropertyDefinition")
        if self.prop.property_type == GeoPropertyDefinition.STRING:
            self.strval = unicode(value)
        elif self.prop.property_type == GeoPropertyDefinition.NUMERIC:
            self.intval = None
            self.decval = None
            if self.prop.num_precision == 0 and abs(int(value)) <= 2147483647:
                self.intval = int(value)
            else:
                self.decval = decimal.Decimal(value)
        elif self.prop.property_type == GeoPropertyDefinition.DATE:
            self.dateval = value
        elif self.prop.property_type == GeoPropertyDefinition.TIME:
            self.timeval = value
        else:
            self.datetimeval = value
    class Meta:
        unique_together=('feature', 'prop')

