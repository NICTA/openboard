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
from django.contrib import admin
from django.conf import settings

from dashboard_loader import views

admin.site.site_url = settings.ADMIN_SITE_URL

urlpatterns = [
    # Views for manually maintaining data
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^$', views.list_widgets, name='list_widget_data'),
    url(r'^parametised_widgets/(?P<widget_url>[^/]+)/(?P<label>[^/]+)$', views.list_widget_params, name="list_widget_params"),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<label>[^/]+)$', views.view_widget, name="view_widget_data"),
    url(r'^parametised_widgets/(?P<widget_url>[^/]+)/(?P<label>[^/]+)/(?P<pval_id>[^/]+)$', views.view_widget, name="view_parametised_widget_data"),
    url(r'^widgets/(?P<widget_url>[^/]+)/(?P<label>[^/]+)/(?P<stat_url>[^/]*)$', 
                        views.edit_stat, name="edit_stat"),
    url(r'^graphs/(?P<widget_url>[^/]+)/(?P<label>[^/]+)/(?P<tile_url>[^/]+)$', 
                        views.edit_graph, name="edit_graph"),
    url(r'^upload/(?P<uploader_app>[^/]+)$', views.upload, name="upload_data"),

    # Views for maintaining users
    url(r'^users/$', views.maintain_users, name="maintain_users"),
    url(r'^users/add_new$', views.add_user, name="add_user"),
    url(r'^users/(?P<username>[^/]+)$', views.edit_user, name="edit_user"),
    url(r'^users/(?P<username>[^/]+)/(?P<action>[^/]+)$', views.user_action, name="user_action"),

    # Admin views (For modifying widget definitions, adding new widgets, etc.)
    url(r'^admin/', include(admin.site.urls)),
]
