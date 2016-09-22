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
import types

from django.shortcuts import render
from django.http import HttpResponse, Http404

def redirect_for_external_view(request, view):
    path = view.external_url + request.path_info
    if request.GET:
        path = path + "?" + urlencode(request.GET)
    return HttpResponseRedirect(path)

class DecimalAwareEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, types.GeneratorType):
            # Limitation of json module. :(
            return list(o)
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


