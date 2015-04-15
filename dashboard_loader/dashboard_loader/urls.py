from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_loader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Views for manually maintaining data
    url(r'^login$', 'dashboard_loader.views.login_view', name='login'),
    url(r'^logout$', 'dashboard_loader.views.logout_view', name='logout'),
    url(r'^$', 'dashboard_loader.views.list_widgets', name='list_widget_data'),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<actual_location_url>[^/]+)/(?P<actual_frequency_url>[^/]+)$', 'dashboard_loader.views.view_widget', name="view_widget_data"),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<actual_location_url>[^/]+)/(?P<actual_frequency_url>[^/]+)/(?P<stat_url>[^/]*)$', 
                        'dashboard_loader.views.edit_stat', name="edit_stat"),
    url(r'^graphs/(?P<widget_url>[^/]+)/(?P<actual_location_url>[^/]+)/(?P<actual_frequency_url>[^/]+)/(?P<tile_url>[^/]+)$', 
                        'dashboard_loader.views.edit_graph', name="edit_graph"),
    url(r'^upload/(?P<uploader_app>[^/]+)$', 'dashboard_loader.views.upload', name="upload_data"),
    # Admin views (For modifying widget definitions, adding new widgets, etc.)
    url(r'^admin/', include(admin.site.urls)),
)
