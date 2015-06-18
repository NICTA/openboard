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
    theme_url = request.GET.get("theme", "")
    try:
        theme = Theme.objects.get(url=theme_url)
    except Theme.DoesNotExist:
        if use_default:
            theme = Theme.objects.all()[0]
        else:
            raise Http404("Theme %s does not exist" % theme_url)
    return theme

def get_location_from_request(request, use_default=False):
    location_url = request.GET.get("location", "")
    try:
        location = Location.objects.get(url=location_url)
    except Location.DoesNotExist:
        if use_default:
            location = Location.objects.all()[0]
        else:
            raise Http404("Location %s does not exist" % location_url)
    return location

def get_frequency_from_request(request, use_default=False):
    frequency_url = request.GET.get("frequency", "")
    try:
        frequency = Frequency.objects.get(url=frequency_url)
    except Frequency.DoesNotExist:
        if use_default:
            frequency = Frequency.objects.all()[0]
        else:
            raise Http404("Frequency %s does not exist" % frequency_url)
    return frequency

def update_maxmin(value, _min, _max):
    if _min is None:
        _min = value
        _max = value
    else:
        _min = min(value, _min)
        _max = max(value, _max)
    return (_min, _max)
