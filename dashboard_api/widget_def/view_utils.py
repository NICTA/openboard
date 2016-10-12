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

import json
import decimal

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseForbidden
from django.views.generic.base import View

from widget_def.models import *
from widget_def.view_tools import *

def get_view_from_request(request):
    return get_view_from_label(request, request.GET.get("view", ""))

def get_view_from_label(request, label):
    try:
        v = WidgetView.objects.get(label=label)
        if v.requires_authentication and not request.user.is_authenticated():
            return None
        return v
    except WidgetView.DoesNotExist:
        raise Http404("<p><b>View %s does not exist</b></p>" % label)

class OpenboardAPIException(Exception):
    def __init__(self, response):
        if isinstance(response, HttpResponse):
            self.response = response
        else:
            self.response = HttpResponseForbidden(u"<p><b>%s</b></p>" % response)

class OpenboardAPIView(View):
    http_method_names =  [ 'get', ]
    lookup_view = False
    lookup_view_explicit_label = False
    set_p3p = False
    def api_method(self, request, **kwargs):
        return {}
    def check_view(self, view):
        pass
    def check_request(self, request):
        pass
    def check_perms(self, request):
        if not settings.PUBLIC_API_ACCESS and not request.user.is_authenticated():
            return False
        else:
            return True
    def get(self, request, *args, **kwargs):
        if not self.check_perms(request):
            return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
        if self.lookup_view:
            if self.lookup_view_explicit_label:
                v = get_view_from_label(request, kwargs.get("view_label"))
            else:
                v = get_view_from_request(request)
            if not v:
                return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
            if v.external_url:
                return redirect_for_external_view(request, v)
        else:
            v = None
        try:
            if v:
                self.check_view(v)
            self.check_request(request)
        except OpenboardAPIException, e:
            return e.response
        json_data = self.api_method(request, view=v)
        return json_list(request, json_data, set_p3p=self.set_p3p)

