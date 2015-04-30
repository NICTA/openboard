from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseForbidden


from widget_def.models import Theme, Location, Frequency
from widget_def.api import *
from widget_def.view_utils import json_list
from widget_def.view_utils import get_theme_from_request, get_location_from_request, get_frequency_from_request

# Views

def get_themes(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_themes())

def get_locations(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_locations())

def get_frequencies(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_frequencies())

def get_icon_libraries(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    return json_list(request, api_get_icon_libraries())

def get_widgets(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    theme = get_theme_from_request(request)
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    return json_list(request, api_get_widgets(theme, location, frequency))

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
                return json_list(request, [], set_p3p=True)
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

