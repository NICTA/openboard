from django.http import HttpResponseNotFound

from widget_def.models import WidgetDeclaration, Statistic
from widget_def.view_utils import json_list
from widget_def.view_utils import get_location_from_request, get_frequency_from_request


# views.

def get_widget_data(request, widget_url):
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    location=location, definition__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    stats_json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget.definition):
        stats_json[statistic.url] = statistic.get_data_json()
    json = {
        "widget_last_updated": widget.definition.last_updated.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "statistics": stats_json,
    }
    return json_list(request, json)

