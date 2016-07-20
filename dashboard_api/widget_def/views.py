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
from django.http.response import HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.conf import settings


from widget_def.models import WidgetView
from widget_def.api import *
from widget_def.view_utils import json_list, redirect_for_external_view
from widget_def.view_utils import get_view_from_label, get_view_from_request

# Views

def get_top_level_views(request):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_top_level_views(request.user))

def get_icon_libraries(request):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_icon_libraries())

def get_view(request, view_label):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    v = get_view_from_label(request, view_label)
    if not v:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    if v.external_url:
        return redirect_for_external_view(request, v)
    return json_list(request, api_get_view(v))

def get_map_layers(request):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_request(request)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    if view.external_url:
        return redirect_for_external_view(request, view)
    hierarchical = request.GET.get("hierarchical")
    if hierarchical in ("", None, "0"):
        hierarchical = False
    else:
        hierarchical = True
    return json_list(request, api_get_map_layers(view, hierarchical))

def get_terria_init(request, view_label, shown_urls=""):
    if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    view = get_view_from_label(request, view_label)
    if view is None:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    if view.external_url:
        return redirect_for_external_view(request, view)
    if not view.geo_window:
        return HttpResponseNotFound("No Geo-window defined for view %s" % view_label)
    if shown_urls:
        shown = shown_urls.split("/")
    else:
        shown = []
    return json_list(request, api_get_terria_init(view, shown))

# Authentication views

def api_login(request):
    username = request.POST.get('username')
    if not username:
        username = request.GET.get('username')
    password = request.POST.get('password')
    if not password:
        password = request.GET.get('password')
    if username and password:
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return json_list(request, request.session.session_key, set_p3p=True)
            else:
                return HttpResponseForbidden("User is inactive")
        else:
            return HttpResponseForbidden("Bad username or password")
    else:
        return HttpResponseForbidden("Username and password not supplied")

def api_logout(request):
    if request.user.is_authenticated():
        logout(request)
    return json_list(request, [])

def api_change_password(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    old_password = request.POST.get('old_password')
    if not old_password:
        old_password = request.GET.get('old_password')
    new_password = request.POST.get('new_password')
    if not new_password:
        new_password = request.GET.get('new_password')
    user = authenticate(username=request.user.username, password=old_password)
    if user:
        user.set_password(new_password)
        user.save()
        login(request, user)
        return json_list(request, [])
    else:
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")

