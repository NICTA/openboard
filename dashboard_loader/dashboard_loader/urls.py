from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_loader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Views for manually maintaining data
    url(r'^widgets$', 'dashboard_loader.views.list_widgets', name='list_widget_data'),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<actual_frequency_url>[^/]+)$', 
                        'dashboard_loader.views.view_widget', name="view_widget_data"),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<actual_frequency_url>[^/]+)/(?P<tile_url>[^/]+)/(?P<stat_url>[^/]*)$', 
                        'dashboard_loader.views.edit_stat', name="edit_stat"),

    # Admin views (For modifying widget definitions, adding new widgets, etc.)
    url(r'^admin/', include(admin.site.urls)),
)
