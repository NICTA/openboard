from widget_def.models import GeoDataset
from widget_data.models import GeoFeature, GeoProperty

from interface import LoaderException

def get_geodataset(url):
    try:
        return GeoDataset.objects.get(url=url)
    except GeoDataset.DoesNotExist:
        raise LoaderException("GeoDataset %s does not exist" % url)

def clear_geodataset(ds):
    GeoFeature.objects.filter(dataset=ds).delete()

def new_geofeature(ds, geom, *args, **kwargs):
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

