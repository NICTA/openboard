from widget_def.models import WidgetFamily, WidgetDefinition, TrafficLightScale, IconLibrary

class ImportExportException(Exception):
    pass

def export_widget(widget):
    if not isinstance(widget, WidgetFamily):
        try:
            widget = WidgetFamily.objects.get(url=widget) 
        except WidgetDefinition.DoesNotExist:
            raise ImportExportException("Widget Family %s does not exist" % (widget))
    return widget.export()

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

def import_class(data):
    if data.get("category"):
        return WidgetFamily
    elif data.get("library_name"):
        return IconLibrary
    elif data.get("scale_name"):
        return TrafficLightScale
    else:
        raise ImportExportException("Unrecognised import class")

def import_data(data):
    cls = import_class(data)
    return cls.import_data(data)

