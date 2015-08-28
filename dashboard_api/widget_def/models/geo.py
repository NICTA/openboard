from widget_def.models import TileDefinition, Location, Theme, Frequency

from django.contrib.gis.db import models

class GeoWindow(models.Model):
    name=models.CharField(max_length=128, 
                    unique=True, help_text="For internal reference only")
    north_east = models.PointField()
    south_west = models.PointField()

class GeoDataset(models.Model):
    POINT = 1
    LINE = 2
    POLYGON = 3
    MULTI_POINT = 4
    MULTI_LINE = 5
    MULTI_POLYGON = 6
    geom_types = ("-", "point", "line", "polygon",
                    "multi-point", "multi-line", "multi-polygon")
    url = models.SlugField(unique=True)
    label = models.CharField(max_length=128)
    subcategory = models.ForeignKey("Subcategory")
    geom_type = models.SmallIntegerField(choices=(
                    (POINT, geom_types[POINT]),
                    (LINE, geom_types[LINE]),
                    (POLYGON, geom_types[POLYGON]),
                    (MULTI_POINT, geom_types[MULTI_POINT]),
                    (MULTI_LINE, geom_types[MULTI_LINE]),
                    (MULTI_POLYGON, geom_types[MULTI_POLYGON]),
                ))
    sort_order = models.IntegerField()
    class Meta:
        unique_together=("subcategory", "sort_order")
        ordering = ("subcategory", "sort_order")

class GeoDatasetDeclaration(models.Model):
    dataset = models.ForeignKey(GeoDataset)
    theme = models.ForeignKey(Theme)
    location = models.ForeignKey(Location)
    frequency = models.ForeignKey(Frequency)
    class Meta:
        unique_together=('dataset', 'theme', 'location', 'frequency')
        ordering = ('dataset', 'theme', 'location', 'frequency')

class GeoPropertyDefinition(models.Model):
    STRING = 1
    NUMERIC = 2
    DATE=3
    TIME=4
    DATETIME=5
    property_types=('-', 'string', 'numeric', 'date', 'time', 'datetime')
    dataset = models.ForeignKey(GeoDataset)
    url = models.SlugField()
    label = models.CharField(max_length=256)
    property_type=models.SmallIntegerField(choices=(
                    (STRING, property_types[STRING]),
                    (NUMERIC, property_types[NUMERIC]),
                    (DATE, property_types[DATE]),
                    (TIME, property_types[TIME]),
                    (DATETIME, property_types[DATETIME]),
                ))
    num_precision=models.SmallIntegerField(blank=True, null=True)
    class Meta:
        unique_together=(('dataset', 'url'), ('dataset', 'label'))

