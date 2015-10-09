import random

from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import GEOSGeometry
from dashboard_loader.loader_utils import *
from widget_def.models import GeoDataset


gda94_srid = 4283
gda94 = SpatialReference(gda94_srid)

def load_geodata(filename, url, **kwargs):
    return call_in_transaction(load_geodata_impl, filename, url, **kwargs)

def load_geodata_impl(filename, url, verbosity=0, 
            simplify=None, dummy_data=None, srid=None, layer_num=0,
            capitalise_properties=False,
            **kwargs):
    messages = []
    ds = get_geodataset(url)
    gdal_ds = DataSource(filename)
    layer = gdal_ds[layer_num]
    if srid:
        if srid != gda94_srid:
            source_ref = SpatialReference(srid)
            xform = CoordTransform(source_ref, gda94)
        else:
            xform = None
    else:
        if layer.srs.srid != gda94_srid:
            xform = CoordTransform(layer.srs, gda94)
        else:
            xform = None
    clear_geodataset(ds)
    features = 0
    total_raw_coords = 0
    total_simp_coords = 0
    for feature in layer:
        geom = feature.geom
        if xform:
            geom.transform(xform)
        if simplify is not None:
            raw_geom = geom.geos
            simp_geom = raw_geom.simplify(tolerance=simplify, preserve_topology=False)
            total_raw_coords += raw_geom.num_coords
            if simp_geom.num_coords < 4:
                if verbosity == 3:
                    messages.append("Keeping raw geometry (%d coords)" % raw_geom.num_coords)
                total_simp_coords += raw_geom.num_coords
            else:
                geom = simp_geom.ogr
                if verbosity == 3:
                    messages.append("Simplified from %d coords to %d coords" % (raw_geom.num_coords, simp_geom.num_coords))
                total_simp_coords += simp_geom.num_coords
        f = new_geofeature(ds, geom)
        for prop in ds.geopropertydefinition_set.all():
            if prop.url == dummy_data:
                set_geoproperty(f, prop, random.randrange(0,101))
            elif capitalise_properties:    
                set_geoproperty(f, prop, feature.get(prop.url.upper()))
            else:    
                set_geoproperty(f, prop, feature.get(prop.url))
        features += 1
    if verbosity > 0:
        messages.append("%d features loaded" % features)
    if verbosity > 1 and simplify is not None:
        messages.append("%d coordinates simplified to %d coordinates" % (
                                    total_raw_coords,
                                    total_simp_coords))
    return messages

