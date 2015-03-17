from django.contrib.auth import authenticate, login
from django.http.response import HttpResponseForbidden

from widget_def.models import *
from widget_def.view_utils import json_list
from widget_def.view_utils import get_theme_from_request, get_location_from_request, get_frequency_from_request

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

def get_icon_libraries(request):
    data = { l.name : l.__getstate__() for l in IconLibrary.objects.all() }
    return json_list(request, data)

def get_widgets(request):
    theme = get_theme_from_request(request)
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    widgets = WidgetDeclaration.objects.filter(theme=theme, location=location, frequency=frequency)
    data = [ w.__getstate__() for w in widgets ]
    return json_list(request, data)

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
                return json_list(request, [])
            else:
                return HttpForbidden("User is inactive")
        else:
            return HttpForbidden("Bad username or password")
    else:
        return HttpForbidden("Username and password not supplied")
