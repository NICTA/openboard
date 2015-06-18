from widget_def.models import WidgetFamily, WidgetDefinition, TrafficLightScale, IconLibrary, PointColourMap
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
    for wd in defs:
        if wd.widgetdeclaration_set.all().count() > 0:
            wdata = {
                "actual_location": wd.actual_location.url,
                "actual_frequency": wd.actual_frequency.url,
                "data": api_get_widget_data(wd),
                "graph_data": api_get_graph_data(wd),
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

def import_class(data):
    if data.get("category"):
        return WidgetFamily
    elif data.get("library_name"):
        return IconLibrary
    elif data.get("scale_name"):
        return TrafficLightScale
    elif data.get("map"):
        return PointColourMap
    else:
        raise ImportExportException("Unrecognised import class")

def import_data(data):
    cls = import_class(data)
    return cls.import_data(data)

