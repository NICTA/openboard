from widget_def.models import *
from widget_def.view_utils import update_maxmin

def api_get_widget_data(widget):
    stats_json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget):
        stats_json[statistic.url] = statistic.get_data_json()
    last_updated = widget.data_last_updated()
    if last_updated:
        last_updated_str = last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
    else:
        last_updated_str = None
    return {
        "widget_last_updated": last_updated_str,
        "actual_frequency": widget.actual_frequency_display(),
        "statistics": stats_json,
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

    return graph_json
