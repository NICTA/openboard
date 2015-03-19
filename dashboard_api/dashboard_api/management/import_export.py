from widget_def.models import WidgetDefinition, TrafficLightScale, IconLibrary

class ImportExportException(Exception):
    pass

def export_widget(widget, actual_location_url, actual_frequency_url=None):
    if not isinstance(widget, WidgetDefinition):
        if not actual_location_url:
            raise ImportExportException("Must pass actual_location_url when exporting widget by url")
        if not actual_frequency_url:
            raise ImportExportException("Must pass actual_frequency_url when exporting widget by url")
        try:
            widget = WidgetDefinition.objects.get(url=widget, 
                                actual_frequency__url=actual_frequency_url,
                                actual_location__url=actual_location_url)
        except WidgetDefinition.DoesNotExist:
            raise ImportExportException("Widget %s:(%s,%s) does not exist" % (widget, actual_location_url, actual_frequency_url))
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
        return WidgetDefinition
    elif data.get("library_name"):
        return IconLibrary
    elif data.get("scale_name"):
        return TrafficLightScale
    else:
        raise ImportExportException("Unrecognised import class")

def import_data(data):
    cls = import_class(data)
    return cls.import_data(data)

