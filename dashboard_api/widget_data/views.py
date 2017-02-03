#   Copyright 2015,2016 CSIRO
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
from widget_def.view_utils import json_list, get_view_from_request, redirect_for_external_view
from widget_def.view_utils import OpenboardAPIView, OpenboardAPIException
from widget_data.api import *

# views.

class GetWidgetDataView(OpenboardAPIView):
    lookup_view = True
    lookup_widget = True
    def api_method(self, request):
        return api_get_widget_data(self.widget, self.view)

class GraphViewBase(OpenboardAPIView):
    lookup_view = True
    def check_request(self, request):
        form = request.GET.get("form", "terse")
        if form == "terse":
            self.verbose = False
        elif form == "verbose":
            self.verbose = True
        else:
            raise OpenboardAPIException(HttpResponseNotFound("<p><b>Unknown form requested.</b></p>"))
 
class GetGraphDataView(GraphViewBase):
    lookup_widget = True
    def api_method(self, request):
        return api_get_graph_data(self.widget, 
                            view=self.view, 
                            verbose=self.verbose)

class GetSingleGraphDataView(GraphViewBase):
    def check_request(self, request):
        self.graph = get_graph(view, self.kwargs.get(self.view, "widget_url"), self.kwargs.get("tile_url"))
        if not graph:
            raise OpenboardAPIException(HttpResponseNotFound("<p><b>This graph does not exist.</b></p>"))
        super(GraphViewBase, self).check_request(request)
    def api_method(self, request):
        return api_get_single_graph_data(self.widget, 
                            view=self.view, 
                            verbose=self.verbose)

class GetRawDataView(OpenboardAPIView):
    lookup_view = True
    lookup_widget = True
    def api_method(self, request):
        return api_get_raw_data(self.widget, request, self.kwargs.get("rds_url"), view=self.view)

class MapDataViewBase(OpenboardAPIView):
    lookup_view = True
    def check_request(self, request):
        if not self.window or self.window.view_override:
            view_window = self.view.geo_window
            if not view_window and not self.window:
                raise OpenboardAPIException("No geowindow defined for this request")
            elif view_window:
                self.window = view_window
    def api_method(self, request):
        return api_geo_dataset(request, self.dataset, self.window)

class GetWidgetMapDataView(MapDataViewBase):
    lookup_widget = True
    def check_request(self, request):
        try:
            tile = TileDefinition.objects.get(widget=widget, url=tile_url, tile_type=TileDefinition.MAP)
        except TileDefinition.DoesNotExist:
            raise OpenboardAPIException(HttpResponseNotFound("Map tile %s does not exist" % tile_url))
        try:
            self.dataset = tile.geo_datasets.get(url=geo_dataset_url)
        except GeoDataset.DoesNotExist:
            raise OpenboardAPIException(HttpResponseNotFound("Map layer %s does not exist" % geo_dataset_url))
        self.window = tile.geo_window
        super(GetWidgetMapDataView, self).check_request(self, request)

class GetMapDataView(MapDataViewBase):
    def check_request(self, request):
        self.dataset = get_declared_geodataset(self.kwargs("geo_dataset_url"), view)
        if self.dataset is None:
            raise OpenboardAPIException(HttpResponseNotFound("Map layer %s does not exist" % kwarg.get("geo_dataset_url")))
        super(GetWidgetMapDataView, self).check_request(self, request)

