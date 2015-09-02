from django.apps import apps

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from widget_def.models import TileDefinition, Location, Theme, Frequency

class GeoWindow(models.Model):
    name=models.CharField(max_length=128, 
                    unique=True, help_text="For internal reference only")
    north_east = models.PointField()
    south_west = models.PointField()
    def __getstate__(self):
        return {
            "north": self.north_east.y,
            "south": self.south_west.y,
            "east": self.north_east.x,
            "west": self.south_west.x,
        }
    def export(self):
        return {
            "name": self.name,
            "north": self.north_east.y,
            "south": self.south_west.y,
            "east": self.north_east.x,
            "west": self.south_west.x,
        }
    def __unicode__(self):
        return self.name
    @classmethod
    def import_data(cls, data):
        try:
            win = cls.objects.get(name=data["name"])
        except cls.DoesNotExist:
            win = cls(name=data["name"])
        win.north_east = Point(data["east"], data["north"])
        win.south_west = Point(data["west"], data["south"])
        win.save()
        return win

class GeoDataset(models.Model): 
    # TODO:  geom_type = PREDEFINED
    #        predefined_regions: lga, postcodes, etc as per csv-geo-au
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
    def __unicode__(self):
        return self.url
    def validate(self):
        problems = []
        for prop in self.geopropertydefinition_set.all():
            problems.extend(prop.validate())
        refs = 0
        refs += self.geodatasetdeclaration_set.count()
        refs += self.tiledefinition_set.count()
        if refs == 0:
            problems.append("Geodataset %s is not referenced - no declarations and not used in any map tiles" % self.url)
        for decl in self.geodatasetdeclaration_set.all():
            if not decl.location.geo_window:
                problems.append("Geodataset %s has a declaration for location %s which has no geo-window defined" % (self.url, decl.location.url))
        return problems
    def __getstate__(self):
        return {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "url": self.url,
            "label": self.label,
            "geom_type": self.geom_types[self.geom_type],
            "properties": [ p.__getstate__() for p in self.geopropertydefinition_set.all() ],
        }
    def export(self):
        return {
            "url": self.url,
            "label": self.label,
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "geom_type": self.geom_type,
            "sort_order": self.sort_order,
            "declarations": [ d.export() for d in self.geodatasetdeclaration_set.all() ],
            "properties":   [ p.export() for p in self.geopropertydefinition_set.all() ],
        }
    @classmethod
    def import_data(cls, data):
        try:
            ds = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            ds = cls(url=data["url"])
        ds.label = data["label"]
        ds.geom_type = data["geom_type"]
        ds.sort_order = data["sort_order"]
        Subcategory = apps.get_app_config("widget_def").get_model("Subcategory")
        ds.subcategory = Subcategory.objects.get(name=data["subcategory"], category__name=data["category"])
        for decl in ds.geodatasetdeclaration_set.all():
            decl.delete()
        for d in data["declarations"]:
            GeoDatasetDeclaration.import_data(ds, d)    
        props = []
        for p in data["properties"]:
            prop = GeoPropertyDefinition.import_data(ds, p)
            props.append(prop.url)
        for prop in ds.geopropertydefinition_set.all():
            if prop.url not in props:
                prop.delete()
        return ds
    class Meta:
        unique_together=(("subcategory", "sort_order"), ("subcategory", "label"))
        ordering = ("subcategory", "sort_order")

class GeoDatasetDeclaration(models.Model):
    dataset = models.ForeignKey(GeoDataset)
    theme = models.ForeignKey(Theme)
    location = models.ForeignKey(Location)
    frequency = models.ForeignKey(Frequency)
    def __getstate__(self):
        return self.dataset.__getstate__()
    def export(self):
        return {
            "theme": self.theme.url,
            "location": self.location.url,
            "frequency": self.frequency.url,
        }
    @classmethod
    def import_data(cls, dataset, data):
        decl = cls(dataset=dataset)
        decl.theme = Theme.objects.get(url=data["theme"])
        decl.location = Location.objects.get(url=data["location"])
        decl.frequency = Frequency.objects.get(url=data["frequency"])
        decl.save()
        return decl
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
    sort_order = models.IntegerField()
    def clean(self):
        if self.property_type != self.NUMERIC:
            self.num_precision = None
    def validate(self):
        problems = []
        self.clean()
        self.save()
        if self.property_type == self.NUMERIC and self.num_precision is None:
            problems.append("Numeric property %s of geo-dataset %s does not have a numeric precision defined" % (self.url, self.dataset.url))
        return problems
    def __getstate__(self):
        data = {
            "url": self.url,
            "label": self.label,
            "type": self.property_types[self.property_type],
        }
        if self.property_type == self.NUMERIC:
            data["num_precision"] = self.num_precision
        return data
    def export(self):
        return {
            "type": self.property_type,
            "url": self.url,
            "label": self.label,
            "num_precision": self.num_precision,
            "sort_order": self.sort_order,
        }
    @classmethod
    def import_data(cls, dataset, data):
        try:
            prop = cls.objects.get(dataset=dataset, url=data["url"])
        except cls.DoesNotExist:
            prop = cls(dataset=dataset, url=data["url"])
        prop.label = data["label"]
        prop.property_type = data["type"]
        prop.num_precision = data["num_precision"]
        prop.sort_order = data["sort_order"]
        prop.save()
        return prop
    class Meta:
        unique_together=(('dataset', 'url'), ('dataset', 'label'), ('dataset', 'sort_order'))
        ordering = ('dataset', 'sort_order')
