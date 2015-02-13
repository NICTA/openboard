from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    # Simple list API views
    url(r'^themes/$', 'widget_def.views.get_themes', name='get_themes'),
    url(r'^locations/$', 'widget_def.views.get_locations', name='get_locations'),
    url(r'^frequencies/$', 'widget_def.views.get_frequencies', name='get_frequencies'),
    url(r'^icons/$', 'widget_def.views.get_icon_libraries', name='get_icon_libraries'),

    # Main API view for obtaining widget definitions
    url(r'^widgets/$', 'widget_def.views.get_widgets', name='get_frequencies'),

    # Main Data API view
    url(r'^widgets/(?P<widget_url>[^/]+)$', 'widget_data.views.get_widget_data', name='get_widget_data'),
)
