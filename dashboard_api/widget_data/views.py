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

from decimal import Decimal

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.conf import settings

from widget_def.models import TileDefinition
from widget_def.view_utils import json_list, get_location_from_request, get_frequency_from_request, get_theme_from_request, get_view_from_request
from widget_data.api import *

# views.

def get_widget_data(request, widget_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    widget = get_declared_widget(widget_url, view)
    if widget:
        return json_list(request, api_get_widget_data(widget, view))
    else:
        return HttpResponseNotFound("This Widget does not exist")

def get_graph_data(request, widget_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    widget = get_declared_widget(widget_url, view)
    if widget:
        return json_list(request, api_get_graph_data(widget, view))
    else:
        return HttpResponseNotFound("This Widget does not exist")

def get_raw_data(request, widget_url, rds_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    widget = get_declared_widget(widget_url, view)
    if not widget:
        return HttpResponseNotFound("This Widget does not exist")
    return api_get_raw_data(widget, request, rds_url)

def get_widget_map_data(request, widget_url, tile_url, geo_dataset_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    widget = get_declared_widget(widget_url, view)
    try:
        tile = TileDefinition.objects.get(widget=widget, url=tile_url, tile_type=TileDefinition.MAP)
    except TileDefinition.DoesNotExist:
        return HttpResponseNotFound("Map tile %s does not exist" % tile_url)
    try:
        ds = tile.geo_datasets.get(url=geo_dataset_url)
    except GeoDataset.DoesNotExist:
        return HttpResponseNotFound("Map layer %s does not exist" % geo_dataset_url)
    window = tile.geo_window
    return api_geo_dataset(request, ds, window)

def get_map_data(request, geo_dataset_url):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    ds = get_declared_geodataset(geo_dataset_url, view)
    if ds is None:
        return HttpResponseNotFound("Map layer %s does not exist" % geo_dataset_url)
    if not location.geo_window:
        return HttpResponseNotFound("No Geo Window defined for location %s" % location.url)
    window = location.geo_window
    return api_geo_dataset(request, ds, window)

