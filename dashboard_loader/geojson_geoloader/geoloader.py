from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from dashboard_loader.loader_utils import *
from widget_def.models import GeoDataset

def load_geodata(filename, url, verbosity=0, **kwargs):
    return call_in_transaction(load_geodata_impl, filename, url, verbosity, **kwargs)

def load_geodata_impl(filename, url, verbosity=0, **kwargs):
    messages = []
    ds = get_geodataset(url)
    gdal_ds = DataSource(filename)
    layer = gdal_ds[0]
    clear_geodataset(ds)
    features = 0
    for feature in layer:
        geom = feature.geom
        f = new_geofeature(ds, geom)
        for prop in ds.geopropertydefinition_set.all():
            set_geoproperty(f, prop, feature.get(prop.url))
        features += 1
    if verbosity > 0:
        messages.append("%d features loaded" % features)
    return messages

