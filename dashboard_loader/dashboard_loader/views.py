from django import forms
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from widget_def.models import WidgetDefinition, Statistic, TrafficLightScaleCode, IconCode, GraphDefinition
from widget_data.models import StatisticData, StatisticListItem, GraphData
from dashboard_loader.models import Uploader
from dashboard_loader.permissions import get_editable_widgets_for_user, user_has_edit_permission, user_has_edit_all_permission, get_uploaders_for_user, user_has_uploader_permission
from dashboard_loader.dynform import get_form_class_for_statistic, get_form_class_for_graph
from dashboard_loader.loader_utils import LoaderException, get_update_format, do_upload

# View methods

# Authentication Views
class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="User name")
    password = forms.CharField(max_length=255, widget=forms.widgets.PasswordInput)

def login_view(request):
    error = None
    next_url = request.GET.get("next")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect("list_widget_data")
            else:
                 error = "Sorry, that account has been deactivated"
        else:
             error = "Invalid login"
    form = LoginForm()
    return render(request, "login.html", {
            "next": next_url,
            "form": form,
            "error": error,
            })

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

# Data Editing Views
@login_required
def list_widgets(request):
    editable_widgets = get_editable_widgets_for_user(request.user)
    uploaders = get_uploaders_for_user(request.user)
    if not editable_widgets and not uploaders:
        return HttpResponseForbidden("You do not have permission to edit or upload any dashboard data")
    return render(request, "widget_data/list_widgets.html", {
            "widgets": editable_widgets,
            "uploaders": uploaders
            })

class WidgetDataForm(forms.Form):
    actual_frequency_display_text=forms.CharField(max_length=60)

@login_required
def view_widget(request, widget_url, actual_location_url, actual_frequency_url):
    try:
        w = WidgetDefinition.objects.get(family__url=widget_url, 
                    actual_location__url=actual_location_url,
                    actual_frequency__url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    edit_all = user_has_edit_all_permission(request.user, w)
    if edit_all:
        statistics = Statistic.objects.filter(tile__widget=w)
    else:
        statistics = Statistic.objects.filter(editable=True,tile__widget=w)
    stats = []
    for s in statistics:
        try:
            data = StatisticData.objects.get(statistic=s)
        except StatisticData.DoesNotExist:
            data = None
        listdata = StatisticListItem.objects.filter(statistic=s)
        stats.append({
                "statistic": s,
                "data": data,
                "listdata": listdata,
            })
    graphs = []
    for graph in GraphDefinition.objects.filter(tile__widget=w):
        data = GraphData.objects.filter(graph=graph)
        graphs.append({
                "graph": graph,
                "data": data
                })
    if request.method == "POST":
        form = WidgetDataForm(request.POST)
        if form.is_valid():
            wdata = w.widget_data()
            if not wdata:
                wdata = WidgetData(widget=w)
            wdata.actual_frequency_text = form.cleaned_data["actual_frequency_display_text"]
            wdata.save()
    else:
        form = WidgetDataForm(initial={
                "actual_frequency_display_text": w.actual_frequency_display(),
                })
    return render(request, "widget_data/view_widget.html", {
            "widget": w,
            "stats": stats,
            "graphs": graphs,
            "form": form,
            })

@login_required
def edit_stat(request, widget_url, actual_location_url, actual_frequency_url, stat_url):
    try:
        w = WidgetDefinition.objects.get(family__url=widget_url, 
                    actual_location__url=actual_location_url,
                    actual_frequency__url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    try:
        s = Statistic.objects.get(tile__widget=w, url=stat_url)
    except Statistic.DoesNotExist:
        return HttpResponseNotFound("This Statistic does not exist")
    if not s.editable and not user_has_edit_all_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    form_class = get_form_class_for_statistic(s)
    if s.is_list() or s.rotates:
        form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=4)
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if form.is_valid():
                if s.is_list() or s.rotates:
                    StatisticListItem.objects.filter(statistic=s).delete()
                    for subform in form:
                        fd = subform.cleaned_data
                        if fd and not fd.get("DELETE"):
                            sli = StatisticListItem(statistic=s)
                            if s.is_numeric():
                                if s.num_precision == 0:
                                    sli.intval = fd["value"]
                                else:
                                    sli.decval = fd["value"]
                            else:
                                sli.strval = fd["value"]
                            if s.traffic_light_scale:
                                try:
                                    tlc = TrafficLightScaleCode.objects.get(scale=s.traffic_light_scale, value=fd["traffic_light_code"])
                                except TrafficLightScaleCode.DoesNotExist:
                                    # TODO: handle error - transactions??
                                    tlc = None
                                sli.traffic_light_code = tlc
                            if s.trend:
                                sli.trend = int(fd["trend"])
                            if s.is_kvlist():
                                sli.keyval = fd["label"]
                            if s.is_eventlist():
                                sli.datekey = fd["date"]
                            if s.hyperlinkable:
                                sli.url = fd["url"]
                            sli.sort_order = fd["sort_order"]
                            sli.save()
                    if request.POST.get("submit"):
                        return redirect("view_widget_data", 
                                widget_url=w.family.url, 
                                actual_location_url=w.actual_location.url,
                                actual_frequency_url=w.actual_frequency.url)
                    else:
                        form = form_class(initial=s.initial_form_data())
                else:
                    fd = form.cleaned_data
                    sd = s.get_data()
                    if not sd:
                        sd = StatisticData(statistic=s)
                    if s.is_numeric():
                        if s.num_precision == 0:
                            sd.intval = fd["value"]
                        else:
                            sd.decval = fd["value"]
                    else:
                        sd.strval = fd["value"]
                    if not s.name_as_label:
                        sd.label = fd["label"]
                    if s.traffic_light_scale:
                        try:
                            tlc = TrafficLightScaleCode.objects.get(scale=s.traffic_light_scale, value=fd["traffic_light_code"])
                        except TrafficLightScaleCode.DoesNotExist:
                            # TODO: handle error
                            tlc = None
                        sd.traffic_light_code = tlc
                    if s.icon_library:
                        try:
                            icon = IconCode.objects.get(scale=s.icon_library, value=fd["icon_code"])
                        except IconCode.DoesNotExist:
                            # TODO: handle error
                            icon = None
                        sd.icon_code = icon
                    if s.trend:
                        sd.trend = int(fd["trend"])
                    sd.save()
                    return redirect("view_widget_data", 
                            widget_url=w.family.url, 
                            actual_location_url=w.actual_location.url,
                            actual_frequency_url=w.actual_frequency.url)
                    
        elif request.POST.get("cancel"):
            return redirect("view_widget_data", 
                        widget_url=w.family.url, 
                        actual_location_url=w.actual_location.url,
                        actual_frequency_url=w.actual_frequency.url)
        elif not s.is_list() and request.POST.get("delete"):
            sd = s.get_data()
            if sd:
                sd.delete()
            return redirect("view_widget_data", 
                        widget_url=w.family.url, 
                        actual_location_url=w.actual_location.url,
                        actual_frequency_url=w.actual_frequency.url)
        else:
            form = form_class(initial=s.initial_form_data())
    else:
        form = form_class(initial=s.initial_form_data())

    return render(request, "widget_data/edit_widget.html", {
                "widget": w,
                "statistic": s,
                "form": form
                })

@login_required
def edit_graph(request, widget_url, actual_location_url, actual_frequency_url, tile_url):
    try:
        w = WidgetDefinition.objects.get(family__url=widget_url, 
                        actual_location__url=actual_location_url,
                        actual_frequency__url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    try:
        g = GraphDefinition.objects.get(tile__widget=w, tile__url=tile_url)
    except GraphDefinition.DoesNotExist:
        return HttpResponseNotFound("This Graph does not exist")

    form_class = get_form_class_for_graph(g)
    form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=10)
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if form.is_valid():
                GraphData.objects.filter(graph=g).delete()
                for subform in form:
                    fd = subform.cleaned_data
                    if fd and not fd.get("DELETE"):
                        gd = GraphData(graph=g)
                        gd.value = fd["value"]
                        if g.use_clusters():
                            # Lookup?
                            gd.cluster = fd["cluster"]
                        # Lookup?
                        gd.dataset = fd["dataset"]
                        if g.graph_type == g.LINE:
                            if g.horiz_axis_type == g.NUMERIC:
                                gd.horiz_numericval = fd["horiz_value"]
                            elif g.horiz_axis_type == g.DATE:
                                gd.horiz_dateval = fd["horiz_value"]
                            elif g.horiz_axis_type == g.TIME:
                                gd.horiz_timeval = fd["horiz_value"]
                        gd.save()
                if request.POST.get("submit"):
                    return redirect("view_widget_data", 
                            widget_url=w.family.url, 
                            actual_location_url=w.actual_location.url,
                            actual_frequency_url=w.actual_frequency.url)
                else:
                    form = form_class(initial=g.initial_form_data())
        elif request.POST.get("cancel"):
            return redirect("view_widget_data", 
                        widget_url=w.family.url, 
                        actual_location_url=w.actual_location.url,
                        actual_frequency_url=w.actual_frequency.url)
        else:
            form = form_class(initial=g.initial_form_data())
    else:
        form = form_class(initial=g.initial_form_data())

    return render(request, "widget_data/edit_graph.html", {
                "widget": w,
                "graph": g,
                "form": form
                })

class UploadForm(forms.Form):
    new_actual_frequency_display_value=forms.CharField(max_length=60, required=False)
    file=forms.FileField()

@login_required
def upload(request, uploader_app):
    try:
        uploader = Uploader.objects.get(app=uploader_app)
    except Uploader.DoesNotExist:
        return HttpResponseNotFound("This uploader does not exist")
    if not user_has_uploader_permission(request.user, uploader):
        return HttpResponseForbidden("You do not have permission to upload data for this uploader")
    fmt = get_update_format(uploader_app)
    messages = []
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            messages = handle_uploaded_file(uploader, request.FILES["file"], 
                    form.cleaned_data["new_actual_frequency_display_value"])
            form = UploadForm()
    else:
        form = UploadForm()
    return render(request, "widget_data/upload_data.html", {
            "uploader": uploader,
            "format": fmt,
            "num_sheets": len(fmt["sheets"]),
            "messages": messages,
            "form": form,
            })

def handle_uploaded_file(uploader, uploaded_file, freq_display=None):
    try:
        return do_upload(uploader, uploaded_file, 
                    actual_freq_display=freq_display, verbosity=3)
    except LoaderException, e:
        return [ "Upload Error: %s" % unicode(e) ]

