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

import datetime
import pytz
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.forms.extras import SelectDateWidget

from widget_data.models import StatisticListItem
from dashboard_loader.time_widget import SelectTimeWidget

tz = pytz.timezone(settings.TIME_ZONE)

class SelectDateTimeWidget(forms.MultiWidget):
    """
    MultiWidget = A widget that is composed of multiple widgets.

    This class combines SelectTimeWidget and SelectDateWidget so we have something 
    like SplitDateTimeWidget (in django.forms.widgets), but with Select elements.
    """
    def __init__(self, attrs=None, hour_step=None, minute_step=None, second_step=None, twelve_hr=False, years=range(2000, datetime.datetime.today().year + 5)):
        """ pass all these parameters to their respective widget constructors..."""
        widgets = (SelectDateWidget(attrs=attrs, years=years), SelectTimeWidget(attrs=attrs, hour_step=hour_step, minute_step=minute_step, second_step=second_step, twelve_hr=twelve_hr))
        super(SelectDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if value.tzinfo:
                value = value.astimezone(tz)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

    def compress(self, datalist):
        if not datalist[0] or not datalist[1]:
            return None
        return tz.localize(datetime.datetime.strptime(datalist[0] + "T" + datalist[1],"%Y-%m-%dT%H:%M:%S"))

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.
        
        Returns a Unicode string representing the HTML for the whole lot.
        """
        return u"""<span><table borders="0">
            <tr><td>%s</td></tr>
            <tr><td>%s</td></tr>
        </table></span>
        """ % (rendered_widgets[0], rendered_widgets[1])

    def value_from_datadict(self, data, files, name):
        return self.compress(super(SelectDateTimeWidget, self).value_from_datadict(data, files, name))

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

def clean(self):
    data = self.cleaned_data
    for check in self.clean_checks:
        data = check(self, data)
    return data
    
def get_form_class_for_statistic(stat):
    form_fields = OrderedDict()
    field_count = 0
    clean_checks = []
    if stat.is_kvlist():
        form_fields["label"] = forms.CharField(required=True, max_length=120)
        field_count += 1
    elif stat.use_datekey():
        form_fields["date"] = forms.DateField(required=False, widget=SelectDateWidget(years=range(2000, datetime.date.today().year+5)))
        field_count += 1
        def clean_check_date(self, data):
            if not data["DELETE"]:
                if not data["date"]:
                    self.add_error("datetime", "This field is required")
            return data
        clean_checks.append(clean_check_date)
    elif stat.use_datetimekey():
        form_fields["datetime"] = forms.DateTimeField(required=False, widget=SelectDateTimeWidget)
        field_count += 1
        if stat.use_datetimekey_level():
            form_fields["level"] = forms.ChoiceField(required=True, choices=StatisticListItem.level_choices)
            field_count += 1
        def clean_check_datetime(self, data):
            if not data["DELETE"]:
                if not data["datetime"]:
                    self.add_error("datetime", "This field is required")
            return data
        clean_checks.append(clean_check_datetime)
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
    elif stat.stat_type != stat.NULL_STAT:
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
    if stat.is_data_list():
        if stat.hyperlinkable:
            form_fields["url"] = forms.URLField(required=False)
        form_fields["sort_order"] = forms.IntegerField(required=True)
        field_count += 1
    form_fields["field_count"] = field_count
    form_fields["clean"] = clean
    form_fields["clean_checks"] = clean_checks
    return type(str("Stat_%s_Form" % stat.name), (forms.Form,), form_fields)

def get_override_form_class_for_graph(graph):
    override_datasets = graph.graphdataset_set.filter(dynamic_label=True)
    form_fields = OrderedDict()
    field_count = 0
    for d in override_datasets:
        form_fields["dataset_%s" % d.url] = forms.CharField(
                    label="Dataset %s (%s)" % (d.label, d.url),
                    max_length=200, required=True)
        field_count += 1
    if field_count == 0:
        return None
    return type(str("GraphOverrides_%s_Form" % graph.tile.url), (forms.Form,), form_fields)

def clean_error_bars(self, data):
    if not data["DELETE"] and data.get("dataset"):
        dataset = data["dataset"]
        if dataset.use_error_bars:
            if data.get("err_valmin") is None:
                self.add_error("err_valmin", "Error range required for this dataset")
            if data.get("err_valmax") is None:
                self.add_error("err_valmax", "Error range required for this dataset")
        else:
            if data.get("err_valmin") is not None:
                del data["err_valmin"]
            if data.get("err_valmax") is not None:
                del data["err_valmax"]
    return data

def get_form_class_for_graph(graph):
    form_fields = OrderedDict()
    field_count = 0
    clean_checks = []
    error_bar_datasets = []
    for ds in graph.graphdataset_set.filter(use_error_bars=True):
        error_bar_datasets.append(ds.url)
    form_fields["error_bar_datasets"] = error_bar_datasets
    if graph.use_clusters():
        form_fields["cluster"] = forms.ModelChoiceField(queryset=graph.graphcluster_set.all(), to_field_name="url", required=True)
        field_count += 1
    form_fields["dataset"] = forms.ModelChoiceField(queryset=graph.graphdataset_set.all(), to_field_name="url", required=True)
    field_count += 1
    form_fields["value"] = forms.DecimalField(required=True, decimal_places=4)
    field_count += 1
    if graph.use_numeric_axes():
        form_fields["err_valmin"] = forms.DecimalField(label="Min", required=False, decimal_places=4)
        form_fields["err_valmax"] = forms.DecimalField(label="Max", required=False, decimal_places=4)
        clean_checks.append(clean_error_bars)
        field_count += 2
    if graph.graph_type == graph.LINE:
        if graph.horiz_axis_type == graph.NUMERIC:
            form_fields["horiz_value"] = forms.DecimalField(required=True, decimal_places=4)
        elif graph.horiz_axis_type == graph.DATE:
            form_fields["horiz_value"] = forms.DateField(required=True, widget=SelectDateWidget(years=range(2000,datetime.date.today().year+5)))
        elif graph.horiz_axis_type == graph.TIME:
            form_fields["horiz_value"] = forms.TimeField(required=True, widget=SelectTimeWidget)
        elif graph.horiz_axis_type == graph.DATETIME:
            form_fields["horiz_value"] = forms.DateTimeField(required=True, widget=SelectDateTimeWidget)
        field_count += 1
    form_fields["field_count"] = field_count
    form_fields["clean"] = clean
    form_fields["clean_checks"] = clean_checks
    form_fields["hidable_fields"] = ["Min", "Max"]
    return type(str("Graph_%s_Form" % graph.tile.url), (forms.Form,), 
                        form_fields)  

