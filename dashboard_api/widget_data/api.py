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

from django.conf import settings
from django.db.models import Max, Min
from django.http import HttpResponse, HttpResponseNotFound

from widget_data.models import GeoProperty
from widget_def.models import *
from widget_def.view_utils import update_maxmin, json_list

def get_declared_widget(widget_url, view):
    try:
        decl = ViewWidgetDeclaration.objects.get(view=view,
                                definition__family__url=widget_url)
        return decl.definition
    except ViewWidgetDeclaration.DoesNotExist:
        return None

def get_declared_geodataset(url, view):
    try:
        decl = ViewGeoDatasetDeclaration.objects.get(view=view,
                                dataset__url=url)
        return decl.dataset
    except ViewGeoDatasetDeclaration.DoesNotExist:
        return None

def api_get_widget_data(widget, view):
    stats_json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget):
        stats_json[statistic.url] = statistic.get_data_json(view)
    last_updated = widget.data_last_updated()
    if last_updated:
        last_updated_str = last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
    else:
        last_updated_str = None
    return {
        "widget_last_updated": last_updated_str,
        "actual_frequency": widget.actual_frequency_display(view),
        "data": stats_json,
    }

def api_get_graph_data(widget):
    graph_json = {}
    for graph in GraphDefinition.objects.filter(tile__widget=widget):
        graph_json[graph.tile.url] = { "data": {} }
        if graph.use_clusters():
            for cluster in graph.graphcluster_set.all():
                graph_json[graph.tile.url]["data"][cluster.url] = {}
        else:
            for dataset in graph.graphdataset_set.all():
                graph_json[graph.tile.url]["data"][dataset.url] = []
        numeric_min = None
        numeric_max = None
        numeric2_min = None
        numeric2_max = None
        horiz_min = None
        horiz_max = None
        for gd in graph.get_data():
            if graph.use_numeric_axes():
                if graph.use_secondary_numeric_axis and gd.dataset.use_secondary_numeric_axis:
                    (numeric2_min, numeric2_max)=update_maxmin(gd.value, 
                                numeric2_min, numeric2_max)
                else:
                    (numeric_min, numeric_max)=update_maxmin(gd.value, 
                                numeric_min, numeric_max)
            if not graph.use_clusters():
                (horiz_min, horiz_max) = update_maxmin(gd.horiz_value(),
                                horiz_min, horiz_max)
            if graph.use_clusters():
                graph_json[graph.tile.url]["data"][gd.cluster.url][gd.dataset.url] = gd.value
            else:
                graph_json[graph.tile.url]["data"][gd.dataset.url].append([
                                    gd.horiz_json_value(),
                                    gd.value
                                ])
        if graph.use_numeric_axes():
            graph_json[graph.tile.url]["%s_scale" % graph.numeric_axis_name()] = {
                    "min": numeric_min,
                    "max": numeric_max
            }
            if graph.use_secondary_numeric_axis:
                graph_json[graph.tile.url]["%s_2_scale" % graph.numeric_axis_name()] = {
                        "min": numeric2_min,
                        "max": numeric2_max
                }
        if not graph.use_clusters():
            graph_json[graph.tile.url]["horizontal_axis_scale"] = {
                    "min": graph.jsonise_horiz_value(horiz_min),
                    "max": graph.jsonise_horiz_value(horiz_max)
            }

    return graph_json

def api_get_raw_data(widget, request, rds_url):
    try:
        rds = RawDataSet.objects.get(widget=widget, url=rds_url)
    except RawDataSet.DoesNotExist:
        return HttpResponseNotFound("This Raw Data Set does not exist")
    if "format" in request.GET and request.GET["format"] != "csv":
        return json_list(request, rds.json())
    response = HttpResponse()    
    response['content-type'] = 'application/csv'
    response['content-disposition'] = 'attachment; filename=%s' % rds.filename
    rds.csv(response)
    return response

def api_geo_dataset(request, dataset, window):
    if dataset.is_external():
        raise HttpResponseNotFound("Map layer %s is an external dataset")
    if dataset.geom_type == dataset.PREDEFINED:
        default_fmt = "csv"
    else:
        default_fmt = "json"
    fmt = request.GET.get("format", default_fmt)
    if fmt not in ("json", "html", "csv"):
        return ResponseNotFound("Unrecognised format: %s" % fmt)
    if fmt == "csv":
        if not dataset.terria_prefer_csv():
            return HttpResponseNotFound("CSV format not supported for %s type datasets" % dataset.geom_types[dataset.geom_type])
        headings=request.GET.get("headings", "label")
    else:
        if dataset.geom_type == dataset.PREDEFINED:
            return HttpResponseNotFound("Only CSV format supported for Predefined Geometry datasets")
        headings=request.GET.get("headings", "url")
    if headings not in ("url", "label"):
        return HttpResponseNotFound("Unrecognised headings parameter: %s" % headings)
    if fmt == "csv":
        response = HttpResponse()    
        response['content-type'] = 'application/csv'
        response['content-disposition'] = 'attachment; filename=%s.csv' % dataset.url
        dataset.csv(response, use_urls=(headings=="url"))
        return response
    out = {
        "type": "FeatureCollection",
        "features": []
    }
    feature_set = dataset.geofeature_set.filter(geometry__bboverlaps=window.padded_polygon())
    if dataset.colour_map:
        try:
            data_prop = dataset.geopropertydefinition_set.get(data_property=True)
            colour_tab = dataset.colour_table()
        except GeoPropertyDefinition.DoesNotExist:
            data_prop = None
    else:
        data_prop = None
    for f in feature_set:
        jf = {
            "type": "Feature",
            "geometry": json.loads(f.geometry.geojson),
            "properties": { prop.heading(headings=="url") : prop.json_value() 
                                        for prop in f.geoproperty_set.all() }
        }
        if data_prop:
            try:
                prop = f.geoproperty_set.get(prop=data_prop)
                if dataset.geom_type in (dataset.POLYGON, dataset.MULTI_POLYGON):
                    jf["properties"]["stroke"] = "#101010"
                    jf["properties"]["fill"] = "#" + colour_tab.rgb_html(decimal.Decimal(prop.value()))
                    jf["properties"]["stroke-width"] = 2
                    jf["properties"]["fill-opacity"] = settings.TERRIA_LAYER_OPACITY
                elif dataset.geom_type in (dataset.LINE, dataset.MULTI_LINE):
                    jf["properties"]["stroke"] = "#" + colour_tab.rgb_html(decimal.Decimal(prop.value()))
                    jf["properties"]["stroke-width"] = 2
                    jf["properties"]["stroke-opacity"] = settings.TERRIA_LAYER_OPACITY
                elif dataset.geom_type in (dataset.POINT, dataset.MULTI_POINT):
                    jf["properties"]["marker-color"] = "#" + colour_tab.rgb_html(decimal.Decimal(prop.value()))
            except GeoProperty.DoesNotExist:
                pass
        out["features"].append(jf)
    return json_list(request, out)

