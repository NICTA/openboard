from decimal import Decimal

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.conf import settings

from widget_def.models import TileDefinition
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
    widget = get_declared_widget(widget_url, theme, location, frequency)
    if widget:
        return json_list(request, api_get_widget_data(widget))
    else:
        return HttpResponseNotFound("This Widget does not exist")

def get_graph_data(request, widget_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    widget = get_declared_widget(widget_url, theme, location, frequency)
    if widget:
        return json_list(request, api_get_graph_data(widget))
    else:
        return HttpResponseNotFound("This Widget does not exist")

def get_raw_data(request, widget_url, rds_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    widget = get_declared_widget(widget_url, theme, location, frequency)
    if not widget:
        return HttpResponseNotFound("This Widget does not exist")
    return api_get_raw_data(widget, request, rds_url)

def get_widget_map_data(request, widget_url, tile_url, geo_dataset_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    widget = get_declared_geodataset(widget_url, theme, location, frequency)
    try:
        tile = TileDefinition.objects.get(widget=widget, url=tile_url, tile_type=TileDefinition.MAP)
    except TileDefinition.DoesNotExist:
        return HttpResponseNotFound("This map tile does not exist")
    try:
        ds = tile.geo_datasets.get(url=geo_dataset_url)
    except GeoDataset.DoesNotExist:
        return HttpResponseNotFound("This map layer does not exist")
    window = tile.geo_window
    return api_geo_dataset(request, ds, window)

def get_map_data(request, geo_dataset_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request, use_default=True)
    if theme is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    ds = get_declared_geodataset(geo_dataset_url, theme, location, frequency)
    if ds is None:
        return HttpResponseNotFound("This map layer does not exist")
    window = location.geo_window
    return api_geo_dataset(request, ds, window)

