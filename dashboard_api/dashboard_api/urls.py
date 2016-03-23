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

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    # Authentication API views
    url(r'^login/$', 'widget_def.views.api_login', name='login'),
    url(r'^logout/$', 'widget_def.views.api_logout', name='logout'),
    url(r'^change_password/$', 'widget_def.views.api_change_password', name='change_password'),

    # Simple list API views
    url(r'^top_level_views$', 'widget_def.views.get_top_level_views', name='get_top_level_views'),
    url(r'^themes/$', 'widget_def.views.get_themes', name='get_themes'),
    url(r'^locations/$', 'widget_def.views.get_locations', name='get_locations'),
    url(r'^frequencies/$', 'widget_def.views.get_frequencies', name='get_frequencies'),
    url(r'^icons/$', 'widget_def.views.get_icon_libraries', name='get_icon_libraries'),

    # Main API view for obtaining view definition (including widgets)
    url(r'^view/(?P<view_label>[^/]+)$', 'widget_def.views.get_view', name='get_view'),

    # Old API view for obtaining widget definitions
    # url(r'^widgets/$', 'widget_def.views.get_widgets', name='get_widgets'),

    # Get Map Layers API view
    url(r'^map_layers/$', 'widget_def.views.get_map_layers', name='get_map_layers'),

    # Main Data API view
    url(r'^widgets/(?P<widget_url>[^/]+)$', 'widget_data.views.get_widget_data', name='get_widget_data'),
    # API Graph Data view
    url(r'^widgets/(?P<widget_url>[^/]+)/graph$', 'widget_data.views.get_graph_data', name='get_graph_data'),
    # API Raw Data Set view
    url(r'^widgets/(?P<widget_url>[^/]+)/rawdata/(?P<rds_url>[^/]+)$', 'widget_data.views.get_raw_data', name='get_raw_data'),
    # API Widget Map data view
    url(r'^widgets/(?P<widget_url>[^/]+)/map/(?P<tile_url>)/(?P<geo_dataset_url>[^/]+)/$', 'widget_data.views.get_widget_map_data', name='get_widget_map_data'),
    # API Map data view
    url(r'^map/(?P<geo_dataset_url>[^/]+)/$', 'widget_data.views.get_map_data', name='get_map_data'),
    # Terria/National Map initialisation json
    url(r'^terria_init/(?P<theme_url>[^/]+)/(?P<location_url>[^/]+)/(?P<frequency_url>[^/]+)/(?P<shown_urls>.+)/init.json$',
                        'widget_def.views.get_terria_init',
                        name='get_terria_init'),
    url(r'^terria_init/(?P<theme_url>[^/]+)/(?P<location_url>[^/]+)/(?P<frequency_url>[^/]+)/init.json$',
                        'widget_def.views.get_terria_init',
                        name='get_terria_init'),
    url(r'^terria_init/(?P<location_url>[^/]+)/(?P<frequency_url>[^/]+)/init.json$',
                        'widget_def.views.get_terria_init',
                        name='get_terria_init'),
)
