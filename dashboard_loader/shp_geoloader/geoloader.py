from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from dashboard_loader.loader_utils import *
from widget_def.models import GeoDataset

gda94_srid = 4283
gda94 = SpatialReference(gda94_srid)

def load_geodata(filename, url, verbosity=0):
    return call_in_transaction(load_geodata_impl, filename, url, verbosity)

def load_geodata_impl(filename, url, verbosity=0):
    messages = []
    ds = get_geodataset(url)
    gdal_ds = DataSource(filename)
    layer = gdal_ds[0]
    if layer.srs.srid != gda94_srid:
        xform = CoordTransform(layer.srs, gda94)
    else:
        xform = None
    clear_geodataset(ds)
    features = 0
    for feature in layer:
        geom = feature.geom
        if xform:
            geom.transform(xform)
        f = new_geofeature(ds, geom)
        for prop in ds.geopropertydefinition_set.all():
            set_geoproperty(f, prop, feature.get(prop.url.upper()))
        features +=1
    if verbosity > 1:
        messages.append("%d features loaded" % features)
    return messages

