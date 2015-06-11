from collections import OrderedDict

from django import forms
from django.forms.extras import SelectDateWidget

from dashboard_loader.time_widget import SelectTimeWidget

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
    elif stat.is_eventlist():
        form_fields["date"] = forms.DateField(required=False, widget=SelectDateWidget(year=range(2000, datetime.date.today().year+5)))
        def clean_check_date(self, data):
            if not data["date"]:
                self.add_error("date", "This field is required")
            return data
        clean_checks.append(clean_check_date)
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
    if stat.is_data_list():
        if stat.hyperlinkable:
            form_fields["url"] = forms.URLField(required=False)
        form_fields["sort_order"] = forms.IntegerField(required=True)
        field_count += 1
    form_fields["field_count"] = field_count
    form_fields["clean"] = clean
    form_fields["clean_checks"] = clean_checks
    return type(str("Stat_%s_Form" % stat.name), (forms.Form,), form_fields)

def get_form_class_for_graph(graph):
    form_fields = OrderedDict()
    field_count = 0
    if graph.use_clusters():
        form_fields["cluster"] = forms.ModelChoiceField(queryset=graph.graphcluster_set.all(), to_field_name="url", required=True)
        field_count += 1
    form_fields["dataset"] = forms.ModelChoiceField(queryset=graph.graphdataset_set.all(), to_field_name="url", required=True)
    field_count += 1
    form_fields["value"] = forms.DecimalField(required=True, decimal_places=4)
    field_count += 1
    if graph.graph_type == graph.LINE:
        if graph.horiz_axis_type == graph.NUMERIC:
            form_fields["horiz_value"] = forms.DecimalField(required=True, decimal_places=4)
        elif graph.horiz_axis_type == graph.DATE:
            form_fields["horiz_value"] = forms.DateField(required=True, widget=SelectDateWidget(years=range(2000,datetime.date.today().year+5)))
        elif graph.horiz_axis_type == graph.TIME:
            form_fields["horiz_value"] = forms.TimeField(required=True, widget=SelectTimeWidget)
        field_count += 1
    form_fields["field_count"] = field_count
    return type(str("Graph_%s_Form" % graph.tile.url), (forms.Form,), 
                        form_fields)  

