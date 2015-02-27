from collections import OrderedDict

from django import forms
from django.forms.extras import SelectDateWidget

from widget_def.models import Statistic

# Dynamic data form methods

def clean_traffic_light_code(self):
    data = self.cleaned_data["traffic_light_code"]
    if data=="":
        raise forms.ValidationError("Must set the traffic light code")
    return data

def clean_icon_code(self):
    data = self.cleaned_data["icon_code"]
    if data=="":
        raise forms.ValidationError("Must set the icon code")
    return data

def get_form_class_for_statistic(stat):
    form_fields = OrderedDict()
    field_count = 0
    if stat.is_kvlist():
        form_fields["label"] = forms.CharField(required=True, max_length=120)
        field_count += 1
    elif stat.is_eventlist():
        form_fields["date"] = forms.DateField(required=True, widget=SelectDateWidget)
    elif not stat.name_as_label:
        form_fields["label"] = forms.CharField(required=True, max_length=80)
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
        form_fields["value"] = forms.CharField(max_length=400, required=True)
    field_count += 1
    if stat.traffic_light_scale:
        form_fields["traffic_light_code"] = forms.ChoiceField(
                        choices = stat.traffic_light_scale.choices(allow_null=True))
        form_fields["clean_traffic_light_code"] = clean_traffic_light_code
        field_count += 1
    if stat.icon_library:
        form_fields["icon_code"] = forms.ChoiceField(
                        choices = stat.icon_library.choices(allow_null=True))
        form_fields["clean_icon_code"] = clean_icon_code
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
        if stat.hyperlinkable:
            form_fields["url"] = forms.URLField(required=False)
        form_fields["sort_order"] = forms.IntegerField(required=True)
        field_count += 1
    form_fields["field_count"] = field_count
    return type(str("Stat_%s_Form" % stat.name), (forms.Form,), form_fields)

