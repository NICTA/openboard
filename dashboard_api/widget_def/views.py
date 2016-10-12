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

from urllib import urlencode

from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseNotFound
from django.conf import settings

from widget_def.api import *
from widget_def.view_utils import OpenboardAPIView, OpenboardAPIException

# Views

class GetTopLevelView(OpenboardAPIView):
    def api_method(self, request, **kwargs):
        return api_get_top_level_views(request.user)

class GetIconLibrariesView(OpenboardAPIView):
    def api_method(self, request, **kwargs):
        return api_get_icon_libraries()

class GetViewView(OpenboardAPIView):
    lookup_view = True
    lookup_view_explicit_label = True
    def api_method(self, request, view, **kwargs):
        return api_get_view(view)

class MapViewBase(OpenboardAPIView):
    lookup_view = True
    def check_view(self, view):
        if not view.geo_window:
            raise OpenAPIException(HttpResponseNotFound(u"<p><b>No Geo-window defined for view %s</b></p>" % view.label))

class GetMapLayers(MapViewBase):
    def api_method(self, request, view, **kwargs):
        hierarchical = request.GET.get("hierarchical")
        if hierarchical in ("", None, "0"):
            hierarchical = False
        else:
            hierarchical = True
        return api_get_map_layers(view, hierarchical)

class GetTerriaInitView(MapViewBase):
    lookup_view_explicit_label = True
    def api_method(self, request, view, **kwargs):
        shown_urls = self.kwargs.get("shown_urls", "")
        if shown_urls: 
            shown = shown_urls.split("/")
        else:
            shown = []
        print shown
        return api_get_terria_init(view, shown)

# Authentication views

class GetPostEquivView(OpenboardAPIView):
    post_args = {}
    http_method_names = [ 'get', 'post', ]
    def post(self, request, *args, **kwargs):
        self.post_args = request.POST
        return self.get(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        self.get_args = request.GET
        return super(GetPostEquivView, self).get(request, *args, **kwargs)
    def get_http_arg(self, key):
        val = self.post_args.get(key)
        if not val:
            val = self.get_args.get(key)
        return val

class APILoginView(GetPostEquivView):
    def check_perms(self, request):
        return True
    def check_request(self, request):
        username = self.get_http_arg("username")
        password = self.get_http_arg("password")
        if not username or not password:
            raise OpenboardAPIException("Username and password not supplied")
        user = authenticate(username=username, password=password)
        if user is None:
            raise OpenboardAPIException("Bad username or password")
        if not user.is_active:
            raise OpenboardAPIException("User is inactive")
        login(request, user)
    def api_method(self, request, **kwargs):
        return request.session.session_key

class APILogoutView(OpenboardAPIView):
    def check_perms(self, request):
        return True
    def check_request(self, request):
        if request.user.is_authenticated():
            logout(request)
    def api_method(self,request, **kwargs):
        return []

class APIChangePasswordView(GetPostEquivView):
    def check_perms(self, request):
        return request.user.is_authenticated()
    def check_request(self, request):
        old_password = self.get_http_arg("old_password")
        new_password = self.get_http_arg("new_password")
        user = authenticate(username=request.user.username, password=old_password)
        if not user:
            raise OpenboardAPIException("Access forbidden")
        user.set_password(new_password)
        user.save()
        login(request, user)
    def api_method(self, request, **kwargs):
        return []

