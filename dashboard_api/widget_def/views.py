import json
from django.http import HttpResponse, Http404
from django.shortcuts import render
from widget_def.models import *

# View utility methods

def json_list(request, data):
    fmt = request.GET.get("format", "json")
    if fmt == "html":
        dump = json.dumps(data, indent=4)
        return render(request, "json_api.html", { 'data': dump })
    dump = json.dumps(data, separators=(',',':'))
    return HttpResponse(dump, content_type='application/json')

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
 
# Views

def get_themes(request):
    data = [ t.__getstate__() for t in Theme.objects.all() ]
    return json_list(request, data)

def get_locations(request):
    data = [ l.__getstate__() for l in Location.objects.all() ]
    return json_list(request, data)

def get_frequencies(request):
    data = [ f.__getstate__() for f in Frequency.objects.all() ]
    return json_list(request, data)

def get_widgets(request):
    theme = get_theme_from_request(request)
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    widgets = theme.widgetdeclaration_set.filter(location=location, frequency=frequency)
    data = [ w.__getstate__() for w in widgets ]
    return json_list(request, data)
    
