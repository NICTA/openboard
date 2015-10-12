#   Copyright 2015 NICTA
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

class DecimalAwareEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalAwareEncoder, self).default(o)

def json_list(request, data, set_p3p=False):
    fmt = request.GET.get("format", "json")
    if fmt == "html":
        dump = jsonize(data, True)
        return render(request, "json_api.html", { 'data': dump })
    else:
        dump = jsonize(data)
        response = HttpResponse(dump, content_type='application/json')
        if set_p3p:
            response["p3p"] = 'CP="This is not a P3P policy!"'
        return response

def jsonize(data, html=False):
    if html:
        return json.dumps(data, indent=4, cls=DecimalAwareEncoder)
    else:
        return json.dumps(data, separators=(',',':'), cls=DecimalAwareEncoder)

def get_theme_from_request(request, use_default=False):
    return get_theme_from_url(request, request.GET.get("theme", ""), use_default)

def get_theme_from_url(request, url, use_default=False):
    try:
        theme = Theme.objects.get(url=url)
    except Theme.DoesNotExist:
        if use_default and not url:
            theme = Theme.objects.all()[0]
        else:
            raise Http404("Theme %s does not exist" % url)
    if request.user.is_authenticated():
        # Theme based authentication!
        return theme
    else:
        if theme.requires_authentication:
            return None
        else:
            return theme

def get_location_from_request(request, use_default=False):
    return get_location_from_url(request.GET.get("location", ""))

def get_location_from_url(url, use_default=False):
    try:
        location = Location.objects.get(url=url)
    except Location.DoesNotExist:
        if use_default and not url:
            location = Location.objects.all()[0]
        else:
            raise Http404("Location %s does not exist" % url)
    return location

def get_frequency_from_request(request, use_default=False):
    return get_frequency_from_url(request.GET.get("frequency", ""))

def get_frequency_from_url(url, use_default=False):
    try:
        frequency = Frequency.objects.get(url=url)
    except Frequency.DoesNotExist:
        if use_default and not url:
            frequency = Frequency.objects.all()[0]
        else:
            raise Http404("Frequency %s does not exist" % url)
    return frequency

def update_maxmin(value, _min, _max):
    if _min is None:
        _min = value
        _max = value
    else:
        _min = min(value, _min)
        _max = max(value, _max)
    return (_min, _max)

def csv_escape(s):
    out = s.replace('"', '""')
    if '"' in out or ',' in out:
        return '"%s"' % out
    else:
        return out

    
def max_with_nulls(*args):
    maxargs = []
    for arg in args:
        if arg is not None:
            maxargs.append(arg)
    if len(maxargs) == 0:
        return None
    elif len(maxargs) == 1:
        return maxargs[0]
    else:
        return max(*maxargs)


