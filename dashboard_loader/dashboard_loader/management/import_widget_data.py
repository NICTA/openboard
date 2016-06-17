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

from dashboard_api.management.import_export import ImportExportException
from widget_def.models import *
from dashboard_loader.loader_utils import *

def import_widget_data(data):
    try:
        family = WidgetFamily.objects.get(url=data["family"])
    except WidgetFamily.DoesNotExist:
        raise ImportExportException("Widget Family %s does not exist" % data["family"])
    except Exception, e:
        raise ImportExportException("Invalid import data %s" % repr(data))
    for w in data["widgets"]:
        if "parameters" in w:
            set_actual_frequency_display_text(data["family"], w["label"], data["default_actual_frequency"])
            try:
                wd = WidgetDefinition.objects.get(family=family)
            except WidgetDefinition.DoesNotExist:
                raise ImportExportException("Parametised widget definition %s does not exist" % (family.url))
            pval = get_paramval(wd.parametisation, **w["parameters"])
        else: 
            try:
                wd = WidgetDefinition.objects.get(family=family, label=w["label"])
            except WidgetDefinition.DoesNotExist:
                raise ImportExportException("Widget definition %s (%s) does not exist" % (family.url, w["label"]))
            pval = None
        set_actual_frequency_display_text(data["family"],
                                w["label"],
                                w["data"]["actual_frequency"], 
                                pval=pval)
        for surl, s in w["data"]["data"].items():
            try:
                stat = Statistic.objects.get(tile__widget=wd,
                                url=surl)
            except Statistic.DoesNotExist:
                raise ImportExportException("Statistic %s for widget %s (%s) does not exist" % (
                                surl,
                                data["family"], 
                                w["label"]))
            if stat.is_data_list():
                clear_statistic_list(data["family"],
                                w["label"],
                                surl,
                                pval=pval)
                sort_order = 10
                for item in s:
                    icon = item.get("icon")
                    if icon:
                        icon_code = icon["value"]
                    else:
                        icon_code = None
                    add_statistic_list_item(data["family"],
                                w["label"],
                                surl,
                                item["value"],
                                sort_order,
                                datetimekey=parse_datetime(item.get("datetime")),
                                datetimekey_level=item.get("datetime_level"),
                                datekey=parse_date(item.get("date")),
                                traffic_light_code=item.get("traffic_light"),
                                icon_code=icon_code,
                                trend = item.get("trend"),
                                label = item.get("label"),
                                url = item.get("url"),
                                pval=pval)
                    sort_order += 10
            else:
                icon = s.get("icon")
                if icon:
                    icon_code = icon["value"]
                else:
                    icon_code = None
                set_statistic_data(data["family"],
                                w["label"],
                                surl,
                                s["value"],
                                traffic_light_code=s.get("traffic_light"),
                                icon_code=icon_code,
                                trend = s.get("trend"),
                                label = s.get("label"),
                                pval=pval)
        for gurl, g in w["graph_data"].items():
            try:
                graph = GraphDefinition.objects.get(tile__widget=wd, tile__url=gurl)
            except GraphDefinition.DoesNotExist:
                raise ImportExportException("Graph %s for widget %s(%s) does not exist" % (
                                    gurl,
                                    data["family"], 
                                    w["label"]))
            clear_graph_data(graph, pval=pval)
            for curl, name in g.get("cluster_name_overrides", {}).items():    
                set_cluster_override(graph, curl, name, pval=pval)
            for durl, name in g.get("dataset_name_overrides", {}).items():    
                set_dataset_override(graph, durl, name, pval=pval)
            if graph.use_clusters():
                for curl, c in g["data"].items():
                    for dsurl, ds in c.items():
                        add_graph_data(graph, dsurl, ds, cluster=curl, pval=pval)
            else:
                for dsurl, ds in g["data"].items():
                    for d in ds:
                        hval = d[0]
                        val = d[1]
                        if graph.horiz_axis_type == graph.DATE:
                            hval = parse_date(hval)
                        elif graph.horiz_axis_type == graph.TIME:
                            hval = parse_time(hval)
                        elif graph.horiz_axis_type == graph.DATETIME:
                            hval = parse_datetime(hval)
                        add_graph_data(graph, dsurl, val, horiz_value=hval, pval=pval)
    return family
