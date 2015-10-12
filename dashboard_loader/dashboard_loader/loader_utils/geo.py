#   Copyright 2015 NICTA
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

from widget_def.models import GeoDataset
from widget_data.models import GeoFeature, GeoProperty

from interface import LoaderException

def get_geodataset(url):
    """Lookup a GeoDataset by url"""
    try:
        return GeoDataset.objects.get(url=url)
    except GeoDataset.DoesNotExist:
        raise LoaderException("GeoDataset %s does not exist" % url)

def clear_geodataset(ds):
    """Clear all data for a GeoDataset"""
    GeoFeature.objects.filter(dataset=ds).delete()

def new_geofeature(ds, geom, *args, **kwargs):
    """Add a new geospatial feature to a GeoDataset

ds: The GeoDataset
geom: A GDAL geometry of the correct type for the dataset.

Properties may be set by either positional or keyword arguments,
or individually by calling ther set_geoproperty method.

Returns the newly created feature on success.
"""
    if geom.__class__ not in ds.gdal_datatypes():
        raise LoaderException("Expected geometry type: %s Got %s" % (
                    ds.datatype(),
                    geom.__class__.__name__
                    ))
    feat = GeoFeature(dataset=ds)
    if geom:
        feat.geometry = geom.wkt
    feat.save()
    (proparray, propdict) = ds.prop_array_dict()
    for i in range(len(args)):
        set_geoproperty(feat, proparray[i], args[i])
    for k,v in kwargs.items():
        set_geoproperty(feat, propdict[k], v)
    return feat

def set_geoproperty(feature, prop_def, value):
    """Set a property on geospatial feature.

feature: the GeoFeature object
prop_def: the GeoProperty definition
value: the (new) value for the property.
"""
    try:
        prop = feature.geoproperty_set.get(prop=prop_def)
        if value is None:
            prop.delete()
            return
    except GeoProperty.DoesNotExist:
        if value is None:
            return
        prop = GeoProperty(feature=feature, prop=prop_def)
    try:
        prop.setval(value)
        prop.save()
    except Exception:
        # print "property: %s type: %s value: <%s>" % (prop_def.url, prop_def.property_types[prop_def.property_type], repr(value))
        raise
    return prop

