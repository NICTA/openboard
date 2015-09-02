from django.contrib.gis.gdal import DataSource
from dashboard_loader.loader_utils import *
from widget_def.models import GeoDataset


def load_geodata(filename, url, verbosity=0):
    return call_in_transaction(load_geodata_impl, filename, url, verbosity)

def load_geodata_impl(filename, url, verbosity=0):
    messages = []
    ds = get_geodataset(url)
    gdal_ds = DataSource(filename)
    layer = gdal_ds[0]
    clear_geodataset(ds)
    features = 0
    for feature in layer:
        f = new_geofeature(ds, feature.geom)
        for prop in ds.geopropertydefinition_set.all():
            set_geoproperty(f, prop, feature.get(prop.url.upper()))
        features +=1
    if verbosity > 1:
        messages.append("%d features loaded" % features)
    return messages

