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
    class Meta:
        unique_together=('feature', 'prop')

