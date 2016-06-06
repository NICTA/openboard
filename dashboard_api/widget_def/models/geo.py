#   Copyright 2015,2016 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json
import decimal

from django.apps import apps

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon
import django.contrib.gis.gdal.geometries as geoms

from dashboard_api.validators import validate_html_colour
from widget_def.view_utils import csv_escape, max_with_nulls
from widget_def.models import TileDefinition, Location, Theme, Frequency, WidgetView
from widget_data.models import GeoFeature, GeoProperty
from widget_def.parametisation import parametise_label

class GeoWindow(models.Model):
    name=models.CharField(max_length=128, 
                    unique=True, help_text="For internal reference only")
    north_east = models.PointField()
    south_west = models.PointField()
    view_override = models.BooleanField(default=False)
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
    def __getstate__(self,view=None):
        if self.view_override and view and view.geo_window:
            return view.geo_window.__getstate__()
        else:
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
            "view_override": self.view_override,
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
        win.view_override = data.get("view_override", False)
        win.save()
        return win

class ColourScaleTable(object):
    class Entry(object):
        def __init__(self, mini, maxi, min_rgber, max_rgber):
            self.min = mini
            self.max = maxi
            (self.min_r, self.min_g, self.min_b) = min_rgber.rgb()
            (self.max_r, self.max_g, self.max_b) = max_rgber.rgb()
        def __unicode__(self):
            return "(%s, %s): (%d, %d, %d)->(%d, %d, %d)" % (
                        unicode(self.min),
                        unicode(self.max),
                        self.min_r, self.min_g, self.min_b,
                        self.max_r, self.max_g, self.max_b)
        def __repr__(self):
            return "Entry %s" % unicode(self)
    def __init__(self, gcs, mini=None, maxi=None):
        self._table = []
        self.min = None
        self.max = None
        if gcs.autoscale:
            if mini is None or maxi is None:
                raise Exception("Must provide min and max values for autoscaling table")
            first_p = gcs.geocolourpoint_set.all()[0]
            last_p  = gcs.geocolourpoint_set.order_by('-value')[0]
            if mini == maxi:
                # Degenerate case
                self.add_entry(mini, mini, first_p, first_p)
                return
            prev_p = None
            for p in gcs.geocolourpoint_set.all():
                if prev_p is not None:
                    self.add_entry(
                            (prev_p.value - first_p.value)/(last_p.value - first_p.value)*(maxi-mini) + mini,
                            (p.value - first_p.value)/(last_p.value - first_p.value)*(maxi-mini) + mini,
                            prev_p, p)
                prev_p = p
            self.min = mini
            self.max = maxi
        else:
            # Manual scaling: ignore mini and maxi
            prev_p = None
            for p in gcs.geocolourpoint_set.all():
                if prev_p is None:
                    # Less than manual range
                    self.add_entry(None, p.value, p, p)
                else:
                    self.add_entry(prev_p.value, p.value, prev_p, p)
                prev_p = p
            if prev_p:
                # Greater than manual range
                    self.add_entry(prev_p.value, None, prev_p, prev_p)
    def terria_map(self):
        tab = []
        done = False
        for e in self._table:
            if e.min is not None and e.max is not None :
                tab.append({
                        "offset": e.min,
                        "color": "rgba(%d,%d,%d,1.00)" %  (e.min_r, e.min_g, e.min_b),
                        })
            elif e.max is None:
                tab.append({
                        "offset": e.min,
                        "color": "rgba(%d,%d,%d,1.00)" %  (e.min_r, e.min_g, e.min_b),
                        })
                done = True
        if not done:
            tab.append({
                    "offset": e.max,
                    "color": "rgba(%d,%d,%d,1.00)" %  (e.max_r, e.max_g, e.max_b),
                    })
        return tab
    def add_entry(self, mini, maxi, min_rgber, max_rgber):
        self._table.append(self.Entry(mini, maxi, min_rgber, max_rgber))
    def find_range(self, value):
        for e in self._table:
            if e.min is None:
                if value <= e.max:
                    return e
            elif e.max is None:
                if value >= e.min:
                    return e
            elif value >= e.min and value <= e.max:
                return e
        raise Exception("Colour scale out of range error: %s" % unicode(value))
    def rgb(self, value):
        r = self.find_range(value)
        if r.min is None or r.max is None:
            return (r.min_r, r.min_g, r.min_b)
        return (
                int((value - r.min)/(r.max-r.min)*(r.max_r-r.min_r) + r.min_r),
                int((value - r.min)/(r.max-r.min)*(r.max_g-r.min_g) + r.min_g),
                int((value - r.min)/(r.max-r.min)*(r.max_b-r.min_b) + r.min_b),
        )
    def rgb_html(self, value):
        rgb = self.rgb(value)
        return "%02X%02X%02X" % rgb

class GeoColourScale(models.Model):
    url=models.SlugField(unique=True)
    autoscale=models.BooleanField(default=True)
    def table(self, mini=None, maxi=None):
        return ColourScaleTable(self, mini, maxi)
    def export(self):
        return {
            "url": self.url,
            "autoscale": self.autoscale,
            "points": [ p.export() for p in self.geocolourpoint_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            scale = cls.objects.get(url=data["url"])
        except cls.DoesNotExist:
            scale = cls(url=data["url"])
        scale.autoscale = data["autoscale"]
        scale.save()
        scale.geocolourpoint_set.delete()
        for p in data["points"]:
            GeoColourPoint.import_data(scale, p)
        return scale
    def __unicode__(self):
        return self.url

class GeoColourPoint(models.Model):
    scale=models.ForeignKey(GeoColourScale)
    value=models.DecimalField(max_digits=15, decimal_places=4)
    colour=models.CharField(max_length=6, validators=[validate_html_colour])
    def rgb(self):
        if len(self.colour) == 3:
            return (int(self.colour[0], base=16),
                    int(self.colour[1], base=16),
                    int(self.colour[2], base=16),
            )
        else:
            return (int(self.colour[0:2], base=16),
                    int(self.colour[2:4], base=16),
                    int(self.colour[4:6], base=16),
            )
    def red(self):
        return self.rgb()[0]
    def green(self):
        return self.rgb()[1]
    def blue(self):
        return self.rgb()[2]
    def export(self):
        data = { "colour": self.colour }
        if self.value == self.value.to_integral_value():
            data["value"] = int(self.value)
        else:
            data["value"] = float(self.value)
        return data
    @classmethod
    def import_data(cls, scale, data):
        p = cls(scale=scale, colour=data["colour"])
        p.value = decimal.Decimal("%.4f" % data["value"])
        p.save()
        return p
    class Meta:
        unique_together=[('scale', 'value')]
        ordering=('scale', 'value')

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
    url = models.SlugField(verbose_name="label", unique=True)
    label = models.CharField(verbose_name="name", max_length=128)
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
    colour_map = models.ForeignKey(GeoColourScale, null=True, blank=True)
    sort_order = models.IntegerField()
    def colour_table(self):
        if self.colour_map:
            try:
                data_prop = self.geopropertydefinition_set.get(data_property=True)
                aggs = GeoProperty.objects.filter(feature__dataset=self, prop=data_prop).aggregate(models.Min("intval"), models.Max("intval"), models.Min("decval"), models.Max("decval"))
                intmin = aggs["intval__min"]
                intmax = aggs["intval__max"]
                decmin = aggs["decval__min"]
                decmax = aggs["decval__max"]
                if intmin is not None:
                    if decmin is None:
                        decmin = decimal.Decimal(intmin)
                    elif decmin > decimal.Decimal(intmin): 
                        decmin = decimal.Decimal(intmin)
                if intmax is not None:
                    if decmax is None:
                        decmax = decimal.Decimal(intmax)
                    elif decmax < decimal.Decimal(intmax):
                        decmax = decimal.Decimal(intmax)
                if decmin is None:
                    data_prop = None
                else:
                    return self.colour_map.table(decmin, decmax)
            except models.ObjectDoesNotExist:
                return None
        else:
            return None
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
        refs += self.viewgeodatasetdeclaration_set.count()
        refs += self.tiledefinition_set.count()
        if refs == 0:
            problems.append("Geodataset %s is not referenced - no declarations and not used in any map tiles" % self.url)
        for decl in self.viewgeodatasetdeclaration_set.all():
            if not decl.view.geo_window:
                problems.append("Geodataset %s has a declaration for view %s which has no geo-window defined" % (self.url, decl.view.label))
        return problems
    def data_last_updated(self, update=False):
        if update or not self._lud_cache:
            lud_feature = GeoFeature.objects.filter(dataset=self).aggregate(lud=models.Max('last_updated'))['lud']
            lud_property = GeoProperty.objects.filter(feature__dataset=self).aggregate(lud=models.Max('last_updated'))['lud']
            self._lud_cache = max_with_nulls(lud_feature, lud_property)
        return self._lud_cache
    def __getstate__(self, view=None, parametisation=None):
        state =  {
            "category": self.subcategory.category.name,
            "subcategory": self.subcategory.name,
            "label": self.url,
            "name": parametise_label(parametisation, view, self.label),
            "geom_type": self.geom_types[self.geom_type],
        }
        if self.is_external():
            state["external_url"] = parametise_label(parametisation, view, self.ext_url)
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
            "view_declarations": [ d.export() for d in self.viewgeodatasetdeclaration_set.all() ],
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
        if "declarations" in data:
            print "WARNING: Old-style GeoDataset declarations ignored."
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

# Old style Geodataset declaration
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

class ViewGeoDatasetDeclaration(models.Model):
    dataset = models.ForeignKey(GeoDataset)
    view = models.ForeignKey(WidgetView)
    def __getstate__(self):
        return self.dataset.__getstate__()
    def export(self):
        return self.view.label
    @classmethod
    def import_data(cls, dataset, data):
        try:
            return cls.objects.get(dataset=dataset, view__label=data)
        except cls.DoesNotExist:
            decl = cls(dataset=dataset, view=WidgetView.objects.get(label=data))
            decl.save()
            return decl

class GeoPropertyDefinition(models.Model):
    STRING = 1
    NUMERIC = 2
    DATE=3
    TIME=4
    DATETIME=5
    property_types=('-', 'string', 'numeric', 'date', 'time', 'datetime')
    dataset = models.ForeignKey(GeoDataset)
    url = models.SlugField(verbose_name="label")
    label = models.CharField(verbose_name="name", max_length=256)
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
            "label": self.url,
            "name": self.label,
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
