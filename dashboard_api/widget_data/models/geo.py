import datetime
import decimal

from django.apps import apps
from django.contrib.gis.db import models

class GeoFeature(models.Model):
    dataset = models.ForeignKey("widget_def.GeoDataset")
    geometry = models.GeometryField()

class GeoProperty(models.Model):
    feature = models.ForeignKey(GeoFeature)
    prop = models.ForeignKey("widget_def.GeoPropertyDefinition")
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    dateval = models.DateField(null=True, blank=True)
    timeval = models.TimeField(null=True, blank=True)
    datetimeval = models.DateTimeField(null=True, blank=True)
    def setval(self, value):
        GeoPropertyDefinition = apps.get_app_config("widget_def").get_model("GeoPropertyDefinition")
        if self.prop.property_type == GeoPropertyDefinition.STRING:
            self.strval = unicode(value)
        elif self.prop.property_type == GeoPropertyDefinition.NUMERIC:
            if self.prop.num_precision == 0:
                self.intval = unicode(value)
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

