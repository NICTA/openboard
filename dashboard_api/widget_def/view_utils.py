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

from django.shortcuts import render
from django.http import HttpResponse, Http404

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
        raise Http404("View %s does not exist" % label)

