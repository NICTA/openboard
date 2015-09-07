import json

from django.apps import apps

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon
import django.contrib.gis.gdal.geometries as geoms

from widget_def.view_utils import csv_escape, max_with_nulls
from widget_def.models import TileDefinition, Location, Theme, Frequency
from widget_data.models import GeoFeature, GeoProperty

class GeoWindow(models.Model):
    name=models.CharField(max_length=128, 
                    unique=True, help_text="For internal reference only")
    north_east = models.PointField()
    south_west = models.PointField()
    def padded_polygon(self):
        n = self.north_east.y
        e = self.north_east.x
        s = self.south_west.y
        w = self.south_west.x
        nsdelta = (n-s)*0.1
        wedelta = (e-w)*0.1
        nn = n + nsdelta
        ss = s - nsdelta
        ee = e + wedelta
        ww = w - wedelta
        if nn > 89.0:
            nn = 89.0
        if ss > -89.0:
            ss = -89.0
        if ww < -180.0:
            ww = -180.0
        if ee > 180.0:
            ee = 180.0
        nnww = Point(ww, nn)
        nnee = Point(ee, nn)
        ssee = Point(ee, ss)
        ssww = Point(ww, ss)
        return Polygon([nnee, nnww, ssww, ssee, nnee])
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
    _lud_cache = None
    POINT = 1
    LINE = 2
    POLYGON = 3
    MULTI_POINT = 4
    MULTI_LINE = 5
    MULTI_POLYGON = 6
    PREDEFINED = 7
    EXTERNAL = 8
    geom_types = ("-", "point", "line", "polygon",
                    "multi-point", "multi-line", "multi-polygon",
                    "predefined", "external")
    gdal_datatypes_map = ( None,
                    (geoms.Point,),
                    (geoms.LineString,),
                    (geoms.Polygon,),
                    (geoms.Point, geoms.MultiPoint),
                    (geoms.LineString, geoms.MultiLineString),
                    (geoms.Polygon, geoms.MultiPolygon),
                    [None.__class__], [])
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
                    (PREDEFINED, geom_types[PREDEFINED]),
                    (EXTERNAL, geom_types[EXTERNAL]),
                ))
    ext_url = models.URLField(null=True, blank=True, help_text="For External GeoDatasets only")
    ext_type = models.CharField(max_length=80, blank=True, null=True, help_text="For External GeoDatasets only - used as 'type' field in Terria catalog.")
    ext_extra = models.CharField(max_length=256, blank=True, null=True, help_text="For External Datasets only - optional extra json for the Terria catalog.  Should be a valid json object if set")
    sort_order = models.IntegerField()
    def is_external(self):
        return self.geom_type == self.EXTERNAL
    def terria_prefer_csv(self):
        return self.geom_type in (self.POINT,self.PREDEFINED)
    def gdal_datatypes(self):
        return self.gdal_datatypes_map[self.geom_type]
    def datatype(self):
        return self.geom_types[self.geom_type]
    def prop_array_dict(self):
        arr = []
        d = {}
        for prop in self.geopropertydefinition_set.all():
            arr.append(prop)
            d[prop.url] = prop
        return (arr, d)
    def __unicode__(self):
        return self.url
    def clean(self):
        if not self.is_external():
            self.ext_url = None
            self.ext_type = None
            self.ext_extra = None
    def validate(self):
        problems = []
        self.clean()
        self.save()
        data_properties = []
        if self.is_external():
            if not self.ext_url:
                problems.append("External Geodataset %s does not have an external URL defined" % self.url)
            if not self.ext_type:
                problems.append("External Geodataset %s does not have an external type defined" % self.url)
            if self.ext_extra:
                try:
                    extra = json.loads(self.ext_extra)
                    d = {}
                    d.update(extra)
                except ValueError:
                    problems.append("Extra JSON for external Geodataset %s is not valid JSON" % self.url)
                except TypeError:
                    problems.append("Extra JSON for external Geodataset %s is not a valid JSON object" % self.url)
        firstprop = True
        for prop in self.geopropertydefinition_set.all():
            if prop.data_property:
                data_properties.append(prop.url)
            problems.extend(prop.validate())
            if self.geom_type == self.PREDEFINED:
                if firstprop and not prop.predefined_geom_property:
                    problems.append("First property %s of Predefined Geometry dataset %s is not a predefined geometry property" % (prop.url, self.url))
                elif not firstprop and prop.predefined_geom_property:
                    problems.append("Predefined geometry property %s of Predefined Geometry dataset %s is not the first property of the dataset" % (prop.url, self.url))
            firstprop = False
        if len(data_properties) > 1:
            problems.append("Geodataset %s has more than one data property: %s" % (self.url, ",".join(data_properties)))
        elif self.geom_type == self.PREDEFINED and len(data_properties) != 1:
            problems.append("Predefined geometry geodataset %s does not have a data property set" % self.url)
        refs = 0
        refs += self.geodatasetdeclaration_set.count()
        refs += self.tiledefinition_set.count()
        if refs == 0:
            problems.append("Geodataset %s is not referenced - no declarations and not used in any map tiles" % self.url)
        for decl in self.geodatasetdeclaration_set.all():
            if not decl.location.geo_window:
                problems.append("Geodataset %s has a declaration for location %s which has no geo-window defined" % (self.url, decl.location.url))
        return problems
    def data_last_updated(self, update=False):
        if update or not self._lud_cache:
            lud_feature = GeoFeature.objects.filter(dataset=self).aggregate(lud=models.Max('last_updated'))['lud']
            lud_property = GeoProperty.objects.filter(feature__dataset=self).aggregate(lud=models.Max('last_updated'))['lud']
            self._lud_cache = max_with_nulls(lud_feature, lud_property)
        return self._lud_cache
    def __getstate__(self):
        state =  {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "url": self.url,
            "label": self.label,
            "geom_type": self.geom_types[self.geom_type],
        }
        if self.is_external():
            state["external_url"] = self.ext_url
            state["external_type"] = self.ext_type
        else:
            state["properties"] = [ 
                    p.__getstate__() 
                    for p in self.geopropertydefinition_set.all() 
            ]
        return state
    def export(self):
        return {
            "url": self.url,
            "label": self.label,
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "geom_type": self.geom_type,
            "ext_url": self.ext_url,
            "ext_type": self.ext_type,
            "ext_extra": self.ext_extra,
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
        ds.ext_url = data.get("ext_url")
        ds.ext_type = data.get("ext_type")
        ds.ext_extra = data.get("ext_extra")
        ds.sort_order = data["sort_order"]
        Subcategory = apps.get_app_config("widget_def").get_model("Subcategory")
        ds.subcategory = Subcategory.objects.get(name=data["subcategory"], category__name=data["category"])
        ds.save()
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
    def csv_header_row(self, use_urls=False):
        if self.geom_type == self.PREDEFINED:
            out = ""
            skip_comma = True
        else:
            out = "lat,lon"
            skip_comma = False
        for prop in self.geopropertydefinition_set.all():
            if skip_comma:
                skip_comma = False
            else:
                out += ","
            if use_urls:
                out += prop.url
            else:
                out += csv_escape(prop.label)
        out += "\n"
        return out
    def csv(self, writer, use_urls=False):
        writer.write(self.csv_header_row(use_urls))
        for f in self.geofeature_set.all():
            writer.write(f.csv())
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
    predefined_geom_property=models.BooleanField(default=False)
    data_property=models.BooleanField(default=False)
    sort_order = models.IntegerField()
    def clean(self):
        if self.property_type != self.NUMERIC:
            self.num_precision = None
        if self.dataset.geom_type != GeoDataset.PREDEFINED:
            self.predefined_geom_property = False
    def validate(self):
        problems = []
        self.clean()
        self.save()
        if self.property_type == self.NUMERIC and self.num_precision is None:
            problems.append("Numeric property %s of geo-dataset %s does not have a numeric precision defined" % (self.url, self.dataset.url))
        if self.data_property and self.property_type != self.NUMERIC:
            problems.append("Non-numeric property %s of geo-dataset %s is marked as a data property" % (self.url, self.dataset.url))
        if self.data_property and self.predefined_geom_property:
            problems.append("Property %s of geo-dataset %s is marked as both a data property and a predefined geometry property." % (self.url, self.dataset.url))
        return problems
    def __getstate__(self):
        data = {
            "url": self.url,
            "label": self.label,
            "type": self.property_types[self.property_type],
        }
        if self.data_property:
            data["class"] = "data"
        elif self.predefined_geom_property:
            data["class"] = "predefined"
        else:
            data["class"] = "other"
        if self.property_type == self.NUMERIC:
            data["num_precision"] = self.num_precision
        return data
    def export(self):
        return {
            "type": self.property_type,
            "url": self.url,
            "label": self.label,
            "data_property": self.data_property,
            "predefined_geom_property": self.predefined_geom_property,
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
        prop.data_property = data.get("data_property", False)
        prop.predefined_geom_property = data.get("predefined_geom_property", False)
        prop.sort_order = data["sort_order"]
        prop.save()
        return prop
    class Meta:
        unique_together=(('dataset', 'url'), ('dataset', 'label'), ('dataset', 'sort_order'))
        ordering = ('dataset', 'sort_order')
