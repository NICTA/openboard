from collections import OrderedDict

from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect
from django import forms

from widget_def.models import WidgetDeclaration, WidgetDefinition, Statistic, TrafficLightScaleCode
from widget_data.models import StatisticData, StatisticListItem
from widget_def.views import json_list, get_location_from_request, get_frequency_from_request

# View utility methods

def get_editable_widgets_for_user(user):
    # TODO: Check permissions
    return WidgetDefinition.objects.all()

def user_has_edit_permission(user, widget):
    # TODO: Check permissions
    return True

def clean_traffic_light_code(self):
    data = self.cleaned_data["traffic_light_code"]
    if data=="":
        raise forms.ValidationError("Must set the traffic light code")
    return data

def getFormClassForStatistic(stat):
    form_fields = OrderedDict()
    field_count = 0
    if stat.stat_type in (Statistic.STRING_KVL, Statistic.NUMERIC_KVL):
        form_fields["label"] = forms.CharField(required=True, max_length=120)
        field_count += 1
    if stat.is_numeric():
        if stat.num_precision == 0:
            form_fields["value"] = forms.IntegerField(required=True)
        else:
            form_fields["value"] = forms.DecimalField(required=True, 
                        decimal_places=stat.num_precision)
    elif stat.stat_type == stat.AM_PM:
        form_fields["value"] = forms.ChoiceField(required=True,
                        choices = ( ("am", "am"), ("pm", "pm") )
                        )
    else:
        form_fields["value"] = forms.CharField(max_length=120, required=True)
    field_count += 1
    if stat.traffic_light_scale:
        form_fields["traffic_light_code"] = forms.ChoiceField(
                        choices = stat.traffic_light_scale.choices(allow_null=True))
        form_fields["clean_traffic_light_code"] = clean_traffic_light_code
        field_count += 1
    if stat.trend:
        form_fields["trend"] = forms.ChoiceField(required=True,
                        choices = (
                            ("1", "Upwards"),
                            ("0", "Steady"),
                            ("-1", "Downwards"),
                        ))
        field_count += 1
    if stat.is_list():
        form_fields["sort_order"] = forms.IntegerField(required=True)
        field_count += 1
    form_fields["field_count"] = field_count
    return type(str("Stat_%s_Form" % stat.name), (forms.Form,), form_fields)

# views.

def get_widget_data(request, widget_url):
    location = get_location_from_request(request)
    frequency = get_frequency_from_request(request)
    try:
        widget = WidgetDeclaration.objects.get(frequency=frequency,
                    location=location, definition__url=widget_url)
    except WidgetDeclaration.DoesNotExist:
        return HttpResponseNotFound("This Widget does not exist")
    json = {}
    for statistic in Statistic.objects.filter(tile__widget=widget.definition):
        json[statistic.name] = statistic.get_data_json()
    return json_list(request, json)

def list_widgets(request):
    editable_widgets = get_editable_widgets_for_user(request.user)
    return render(request, "widget_data/list_widgets.html", {
            "widgets": editable_widgets
            })

def view_widget(request, widget_url, actual_frequency_url):
    try:
        w = WidgetDefinition.objects.get(url=widget_url, 
                    actual_frequency_url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    statistics = Statistic.objects.filter(tile__widget=w)
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
    return render(request, "widget_data/view_widget.html", {
            "widget": w,
            "stats": stats,
            })

def edit_stat(request, widget_url, actual_frequency_url, tile_url, stat_name):
    try:
        w = WidgetDefinition.objects.get(url=widget_url, actual_frequency_url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    try:
        s = Statistic.objects.get(tile__widget=w, tile__url=tile_url, name=stat_name)
    except Statistic.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")

    form_class = getFormClassForStatistic(s)
    if s.is_list():
        form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=4)
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if form.is_valid():
                if s.is_list():
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
                            if s.stat_type in (s.NUMERIC_KVL, s.STRING_KVL):
                                sli.keyval = fd["label"]
                            sli.sort_order = fd["sort_order"]
                            sli.save()
                    if request.POST.get("submit"):
                        return redirect("view_widget_data", 
                                widget_url=w.url, 
                                actual_frequency_url=w.actual_frequency_url)
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
                    if s.traffic_light_scale:
                        try:
                            tlc = TrafficLightScaleCode.objects.get(scale=s.traffic_light_scale, value=fd["traffic_light_code"])
                        except TrafficLightScaleCode.DoesNotExist:
                            # TODO: handle error
                            tlc = None
                        sd.traffic_light_code = tlc
                    if s.trend:
                        sd.trend = int(fd["trend"])
                    sd.save()
                    return redirect("view_widget_data", 
                            widget_url=w.url, 
                            actual_frequency_url=w.actual_frequency_url)
                    
        elif request.POST.get("cancel"):
            return redirect("view_widget_data", 
                        widget_url=w.url, 
                        actual_frequency_url=w.actual_frequency_url)
        elif not s.is_list() and request.POST.get("delete"):
            sd = s.get_data()
            if sd:
                sd.delete()
            return redirect("view_widget_data", 
                        widget_url=w.url, 
                        actual_frequency_url=w.actual_frequency_url)
        else:
            form = form_class(initial=s.initial_form_data())
    else:
        form = form_class(initial=s.initial_form_data())

    return render(request, "widget_data/edit_widget.html", {
                "widget": w,
                "statistic": s,
                "form": form
                })

