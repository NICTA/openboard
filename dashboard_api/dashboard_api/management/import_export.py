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

from widget_def.models import WidgetFamily, WidgetDefinition, TrafficLightScale, IconLibrary, PointColourMap, GeoWindow, GeoDataset, GeoColourScale, TrafficLightAutoStrategy, TrafficLightAutomation, WidgetView, Parametisation
from widget_def.models.reference import WidgetViews, AllCategories
from widget_data.api import *

class ImportExportException(Exception):
    pass

def sanitise_widget_arg(widget):
    if not isinstance(widget, WidgetFamily):
        try:
            return WidgetFamily.objects.get(url=widget) 
        except WidgetDefinition.DoesNotExist:
            raise ImportExportException("Widget Family %s does not exist" % (widget))
    return widget

def export_widget(widget):
    widget = sanitise_widget_arg(widget)
    return widget.export()

def export_widget_data(widget):
    widget = sanitise_widget_arg(widget)
    defs = WidgetDefinition.objects.filter(family=widget)
    data = { "family": widget.url, "widgets": [] }
    exported_default_actual_freq = False
    for wd in defs:
        if wd.viewwidgetdeclaration_set.all().count() > 0:
            if wd.parametisation:
                for pval in wd.parametisation.parametisationvalue_set.all():
                    if not exported_default_actual_freq:
                        data["default_actual_frequency"] = wd.actual_frequency_display()
                        exported_default_actual_freq = True
                    wdata = {
                        "label": wd.label,
                        "parameters": pval.parameters(),
                        "data": api_get_widget_data(wd, pval=pval),
                        "graph_data": api_get_graph_data(wd, pval=pval),
                        "raw_datasets": None
                    }
                    data["widgets"].append(wdata)
            else:
                wdata = {
                    "label": wd.label,
                    "data": api_get_widget_data(wd),
                    "graph_data": api_get_graph_data(wd),
                    "raw_datasets": None,
                }
                data["widgets"].append(wdata)
    return data

def export_trafficlightscale(scale):
    if not isinstance(scale, TrafficLightScale):
        try:
            scale = TrafficLightScale.objects.get(name=scale)
        except TrafficLightScale.DoesNotExist:
            raise ImportExportException("TrafficLightScale %s does not exist" % scale)
    return scale.export()

def export_trafficlightstrategy(strategy):
    if not isinstance(strategy, TrafficLightAutoStrategy):
        try:
            strategy = TrafficLightAutoStrategy.objects.get(url=strategy)
        except TrafficLightAutoStrategy.DoesNotExist:
            raise ImportExportException("TrafficLightAutoStrategy %s does not exist" % strategy)
    return strategy.export()

def export_trafficlightautomation(tla):
    if not isinstance(tla, TrafficLightAutomation):
        try:
            tla = TrafficLightAutomation.objects.get(url=tla)
        except TrafficLightAutomation.DoesNotExist:
            raise ImportExportException("TrafficLightAutomation %s does not exist" % tla)
    return tla.export()

def export_iconlibrary(library):
    if not isinstance(library, IconLibrary):
        try:
            library = IconLibrary.objects.get(name=library)
        except IconLibrary.DoesNotExist:
            raise ImportExportException("IconLibrary %s does not exist" % library)
    return library.export()

def export_pointcolourmap(pcm):
    if not isinstance(pcm, PointColourMap):
        try:
            pcm = PointColourMap.objects.get(label=pcm)
        except PointColourMap.DoesNotExist:
            raise ImportExportException("PointColourMap %s does not exist" % pcm)
    return pcm.export()

def export_geowindow(win):
    if not isinstance(win, GeoWindow):
        try:
            win = GeoWindow.objects.get(name=win)
        except GeoWindow.DoesNotExist:
            raise ImportExportException('GeoWindow "%s" does not exist' % pcm)
    return win.export()

def export_geodataset(ds):
    if not isinstance(ds, GeoDataset):
        try:
            ds = GeoDataset.objects.get(url=ds)
        except GeoDataset.DoesNotExist:
            raise ImportExportException('GeoDataset "%s" does not exist' % ds)
    return ds.export()

def export_geocolourscale(gcs):
    if not isinstance(gcs, GeoColourScale):
        try:
            gcs = GeoColourScale.objects.get(url=gcs)
        except GeoColourScale.DoesNotExist:
            raise ImportExportException('GeoColourScale "%s" does not exist' % gcs)
    return gcs.export()

def export_widget_view(v):
    if not isinstance(v, WidgetView):
        try:
            v = WidgetView.objects.get(label=v)
        except WidgetView.DoesNotExist:
            raise ImportExportException('WidgetView "%s" does not exist' % v)
    if v.parent is not None:
        raise ImportExportException('Can only export top-level Widget Views')
    return v.export()

def export_parametisation(p):
    if not isinstance(p, Parametisation):
        try:
            p = Parametisation.objects.get(url=p)
        except Parametisation.DoesNotExist:
            raise ImportExportException('Parametisation "%s" does not exist' % p)
    if not p.keys():
        raise ImportExportException('Parametisation "%s" has no keys' % unicode(p))
    return p.export()

def export_views():
    return WidgetViews().export()
            
def export_categories():
    return Category().export_all()
            
def import_class(data):
    if data.get("children") is not None:
        return WidgetView
    elif data.get("strategy"):
        return TrafficLightAutomation
    elif data.get("rules"):
        return TrafficLightAutoStrategy
    elif data.get("autoscale"):
        return GeoColourScale
    elif data.get("geom_type"):
        return GeoDataset
    elif data.get("category"):
        return WidgetFamily
    elif data.get("library_name"):
        return IconLibrary
    elif data.get("scale_name"):
        return TrafficLightScale
    elif data.get("map"):
        return PointColourMap
    elif data.get("themes"):
        return WidgetViews
    elif data.get("categories"):
        return AllCategories
    elif data.get("north"):
        return GeoWindow
    elif data.get("keys"):
        return Parametisation
    else:
        raise ImportExportException("Unrecognised import class")

def import_data(data, merge=False):
    cls = import_class(data)
    try:
        if cls in (AllCategories, WidgetViews):
            return cls.import_data(data, merge)
        else:
            return cls.import_data(data)
    except Exception, e:
        raise ImportExportException("Import error: %s" % repr(e))

