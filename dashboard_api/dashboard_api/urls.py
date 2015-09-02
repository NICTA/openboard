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
    url(r'^themes/$', 'widget_def.views.get_themes', name='get_themes'),
    url(r'^locations/$', 'widget_def.views.get_locations', name='get_locations'),
    url(r'^frequencies/$', 'widget_def.views.get_frequencies', name='get_frequencies'),
    url(r'^icons/$', 'widget_def.views.get_icon_libraries', name='get_icon_libraries'),

    # Main API view for obtaining widget definitions
    url(r'^widgets/$', 'widget_def.views.get_widgets', name='get_frequencies'),

    # Get Map Layers API view
    url(r'^map_layers/$', 'widget_def.views.get_map_layers', name='get_map_layers'),

    # Main Data API view
    url(r'^widgets/(?P<widget_url>[^/]+)$', 'widget_data.views.get_widget_data', name='get_widget_data'),
    # API Graph Data view
    url(r'^widgets/(?P<widget_url>[^/]+)/graph$', 'widget_data.views.get_graph_data', name='get_graph_data'),
    # API Raw Data Set view
    url(r'^widgets/(?P<widget_url>[^/]+)/rawdata/(?P<rds_url>[^/]+)$', 'widget_data.views.get_raw_data', name='get_raw_data'),
)
