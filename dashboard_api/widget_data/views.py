from decimal import Decimal

from django.http import HttpResponseNotFound

from widget_def.models import WidgetDeclaration, Statistic, GraphDefinition
from widget_def.view_utils import json_list
from widget_def.view_utils import get_location_from_request, get_frequency_from_request, update_maxmin


# views.

def get_widget_data(request, widget_url):
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    location=location, definition__family__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    stats_json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget.definition):
        stats_json[statistic.url] = statistic.get_data_json()
    json = {
        "widget_last_updated": widget.definition.data_last_updated().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "statistics": stats_json,
    }
    return json_list(request, json)

def get_graph_data(request, widget_url):
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    location=location, definition__family__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    graph_json = {}
    for graph in GraphDefinition.objects.filter(tile__widget=widget.definition):
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
            graph_json[graph.tile.url]["vertical_axis_scale"] = {
                    "min": numeric_min,
                    "max": numeric_max
            }
            if graph.use_secondary_numeric_axis:
                graph_json[graph.tile.url]["vertical_axis_scale"] = {
                        "min": numeric2_min,
                        "max": numeric2_max
                }
        if not graph.use_clusters():
            graph_json[graph.tile.url]["horizontal_axis_scale"] = {
                    "min": graph.jsonise_horiz_value(horiz_min),
                    "max": graph.jsonise_horiz_value(horiz_max)
            }

    return json_list(request, graph_json)
