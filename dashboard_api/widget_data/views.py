from decimal import Decimal

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.conf import settings

from widget_def.models import WidgetDeclaration, RawDataSet
from widget_def.view_utils import json_list, get_location_from_request, get_frequency_from_request, get_theme_from_request
from widget_data.api import *

# views.

def get_widget_data(request, widget_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency, 
                    theme=theme,
                    location=location, 
                    definition__family__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    return json_list(request, api_get_widget_data(widget.definition))

def get_graph_data(request, widget_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    theme=theme,
                    location=location, 
                    definition__family__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    return json_list(request, api_get_graph_data(widget.definition))

def get_raw_data(request, widget_url, rds_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    theme=theme,
                    location=location, 
                    definition__family__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    try:
        rds = RawDataSet.objects.get(widget=widget.definition, url=rds_url)
    except RawDataSet.DoesNotExist:
        return HttpResponseNotFound("This Raw Data Set does not exist")
    response = HttpResponse()    
    response['content-type'] = 'application/csv'
    response['content-disposition'] = 'attachment; filename=%s' % rds.filename
    response.write(rds.csv())
    return response

