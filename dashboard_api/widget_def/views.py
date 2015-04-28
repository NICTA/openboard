from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseForbidden


from widget_def.models import *
from widget_def.view_utils import json_list
from widget_def.view_utils import get_theme_from_request, get_location_from_request, get_frequency_from_request

# Views

def get_themes(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    data = [ t.__getstate__() for t in Theme.objects.all() ]
    return json_list(request, data)

def get_locations(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    data = [ l.__getstate__() for l in Location.objects.all() ]
    return json_list(request, data)

def get_frequencies(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    data = [ f.__getstate__() for f in Frequency.objects.filter(display_mode=True) ]
    return json_list(request, data)

def get_icon_libraries(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
    data = { l.name : l.__getstate__() for l in IconLibrary.objects.all() }
    return json_list(request, data)

def get_widgets(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<p><b>Access forbidden</b></p>")
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

