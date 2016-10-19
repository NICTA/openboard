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

from django.conf.urls import include, url
from widget_def import views as wdef_views
from widget_data import views as wdata_views

urlpatterns = [
    # Authentication API views
    url(r'^login/$', wdef_views.APILoginView.as_view(), name='login'),
    url(r'^logout/$', wdef_views.APILogoutView.as_view(), name='logout'),
    url(r'^change_password/$', wdef_views.APIChangePasswordView.as_view(), name='change_password'),

    # Simple list API views
    url(r'^top_level_views$', wdef_views.GetTopLevelView.as_view(), name='get_top_level_views'),
    url(r'^icons/$', wdef_views.GetIconLibrariesView.as_view(), name='get_icon_libraries'),

    # Main API view for obtaining view definition (including widgets)
    url(r'^view/(?P<view_label>[^/]+)$', wdef_views.GetViewView.as_view(), name='get_view'),

    # Get Map Layers API view
    url(r'^map_layers/$', wdef_views.GetMapLayers.as_view(), name='get_map_layers'),

    # Main Data API view
    url(r'^widgets/(?P<widget_url>[^/]+)$', wdata_views.GetWidgetDataView.as_view(), name='get_widget_data'),
    # API Graph Data views
    url(r'^widgets/(?P<widget_url>[^/]+)/graph$', wdata_views.GetGraphDataView.as_view(), name='get_graph_data'),
    url(r'^widgets/(?P<widget_url>[^/]+)/graph/(?P<tile_url>[^/]+)$', wdata_views.GetSingleGraphDataView.as_view(), name='get_graph_data'),
    # API Raw Data Set view
    url(r'^widgets/(?P<widget_url>[^/]+)/rawdata/(?P<rds_url>[^/]+)$', wdata_views.GetRawDataView.as_view(), name='get_raw_data'),
    # API Widget Map data view
    url(r'^widgets/(?P<widget_url>[^/]+)/map/(?P<tile_url>)/(?P<geo_dataset_url>[^/]+)/$', wdata_views.GetWidgetMapDataView.as_view(), name='get_widget_map_data'),
    # API Map data view
    url(r'^map/(?P<geo_dataset_url>[^/]+)/$', wdata_views.GetMapDataView.as_view(), name='get_map_data'),

    # Terria/National Map initialisation json
    url(r'^terria_init/(?P<view_label>[^/]+)/(?P<shown_urls>.+)/init.json$',
                        wdef_views.GetTerriaInitView.as_view(),
                        name='get_terria_init'),
    url(r'^terria_init/(?P<view_label>[^/]+)/init.json$',
                        wdef_views.GetTerriaInitView.as_view(),
                        name='get_terria_init'),
]
