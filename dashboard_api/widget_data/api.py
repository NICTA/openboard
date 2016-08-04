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

from widget_data.models import GeoProperty, GraphClusterData, GraphDatasetData
from widget_def.models import *
from widget_def.view_utils import update_maxmin, json_list
from widget_def.parametisation import resolve_pval, parametise_label

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

def get_graph(view, widget_url, tile_url):
    widget = get_declared_widget(widget_url, view)
    try:
        return GraphDefinition.objects.get(tile__widget=widget, tile__url=tile_url)
    except GraphDefinition.DoesNotExist:
        return None

def api_get_widget_data(widget, view=None, pval=None):
    stats_json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget):
        stats_json[statistic.url] = statistic.get_data_json(view=view, pval=pval)
    last_updated = widget.data_last_updated(view=view, pval=pval)
    if last_updated:
        last_updated_str = last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
    else:
        last_updated_str = None
    widget_data=widget.widget_data(view=view, pval=pval)
    data = {
        "widget_last_updated": last_updated_str,
        "data": stats_json,
    }
    data["actual_frequency"] = widget.actual_frequency_display(wd=widget_data)
    if widget_data:
        data["text_block"] = widget_data.text_block
    else:
        data["text_block"] = None
    return data

def api_get_graph_data(widget, view, verbose=False):
    pval = resolve_pval(widget.parametisation, view=view)
    graph_json = {}
    for graph in GraphDefinition.objects.filter(tile__widget=widget):
        graph_json[graph.tile.url] = api_get_single_graph_data(graph, pval=pval, verbose=verbose)
    return graph_json

def api_get_single_graph_data(graph, view, pval=None, verbose=False):
    pval = resolve_pval(graph.widget().parametisation, view=view, pval=pval)
    graph_json = { "data": {} }
    if verbose:
        graph_json["data"] = []
    else:
        if graph.use_clusters():
            for cluster in graph.graphcluster_set.all():
                graph_json["data"][cluster.url] = {}
        else:
            for dataset in graph.graphdataset_set.all():
                graph_json["data"][dataset.url] = []
    numeric_min = None
    numeric_max = None
    numeric2_min = None
    numeric2_max = None
    horiz_min = None
    horiz_max = None
    for gd in graph.get_data(pval=pval):
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
        if verbose:
            if graph.use_numeric_axes():
                if gd.dataset.use_secondary_numeric_axis:
                    data_label = graph.secondary_numeric_axis_label
                else:
                    data_label = graph.numeric_axis_label
                data_label = parametise_label(graph.widget(), view, data_label)
            else:
                data_label = "value"
            graph_datum = {
                    parametise_label(graph.widget(), view, graph.dataset_label): parametise_label(graph.widget(), view, get_graph_subset_displayname(gd.dataset,pval)),
                    data_label: gd.value
                    }
            if graph.use_clusters():
                graph_datum[parametise_label(graph.widget(), view, graph.cluster_label)] = parametise_label(graph.widget(), view, get_graph_subset_displayname(gd.cluster,pval))
            else:
                graph_datum[parametise_label(graph.widget(), view, graph.horiz_axis_label)] = gd.horiz_json_value()
            if gd.dataset.use_error_bars:
                graph_datum[data_label + "_min"] = gd.err_valmin
                graph_datum[data_label + "_max"] = gd.err_valmax
            graph_json["data"].append(graph_datum)
        else:
            if gd.dataset.use_error_bars:
                json_val = {
                            "value": gd.value,
                            "min": gd.err_valmin,
                            "max": gd.err_valmax,
                }
            else:
                json_val = gd.value
            if graph.use_clusters():
                graph_json["data"][gd.cluster.url][gd.dataset.url] = json_val
            else:
                json_val["horizontal_value"] = gd.horiz_json_value()
                graph_json["data"][gd.dataset.url].append(json_val)
    if graph.use_numeric_axes():
        graph_json["%s_scale" % graph.numeric_axis_name()] = {
                "min": numeric_min,
                "max": numeric_max
        }
        if graph.use_secondary_numeric_axis:
            graph_json["%s_2_scale" % graph.numeric_axis_name()] = {
                    "min": numeric2_min,
                    "max": numeric2_max
            }
    if not graph.use_clusters():
        graph_json["horizontal_axis_scale"] = {
                "min": graph.jsonise_horiz_value(horiz_min),
                "max": graph.jsonise_horiz_value(horiz_max)
        }
    overrides = get_graph_overrides(graph.graphcluster_set, GraphClusterData, "cluster", pval)
    if overrides:
        graph_json["cluster_name_overrides"] = overrides
    overrides = get_graph_overrides(graph.graphdataset_set, GraphDatasetData, "dataset", pval)
    if overrides:
        graph_json["dataset_name_overrides"] = overrides
    return graph_json

def get_graph_subset_displayname(dataset_or_cluster, pval):
    if dataset_or_cluster.dynamic_label:
        ds = None
        if isinstance(dataset_or_cluster, GraphCluster):
            try:
                ds = GraphClusterData.objects.get(param_value=pval, cluster=dataset_or_cluster)
            except GraphClusterData.DoesNotExist:
                pass
        else:
            try:
                ds = GraphDatasetData.objects.get(param_value=pval, dataset=dataset_or_cluster)
            except GraphDatasetData.DoesNotExist:
                pass
        if ds:
            return ds.display_name

    return dataset_or_cluster.label

def get_graph_overrides(query, clazz, key, pval):
    overrides = {}
    for obj in query.filter(dynamic_label=True):
        try:
            kwargs = {
                key: obj,
                "param_value": pval
            }
            dobj = clazz.objects.get(**kwargs)
            overrides[obj.url] = dobj.display_name
        except clazz.DoesNotExist:
            pass
    return overrides

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

