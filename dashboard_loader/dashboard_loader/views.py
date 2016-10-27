#   Copyright 2015,2016 CSIRO
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

from django import forms
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import FormView
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from widget_def.models import WidgetDefinition, Statistic, TrafficLightScaleCode, IconCode, GraphDefinition, ParametisationValue
from widget_data.models import WidgetData, StatisticData, StatisticListItem, GraphData, DynamicGraphCluster
from dashboard_loader.models import Uploader
from dashboard_loader.permissions import get_editable_widgets_for_user, user_has_edit_permission, user_has_edit_all_permission, get_uploaders_for_user, user_has_uploader_permission
from dashboard_loader.dynform import get_form_class_for_statistic, get_form_class_for_graph, get_override_form_class_for_graph, DynamicGraphClusterForm
from dashboard_loader.loader_utils import *

# View methods

# Authentication Views
class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="User name")
    password = forms.CharField(max_length=255, widget=forms.widgets.PasswordInput)

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('list_widget_data')
    error = None
    def form_valid(self, form):
        username = self.request.POST["username"]
        password = self.request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                next_url = self.request.GET.get("next")
                if next_url:
                    self.success_url = next_url
                return super(LoginView, self).form_valid(form)
            else:
                 self.error = "Sorry, that account has been deactivated"
        else:
             self.error = "Invalid login"
        return self.form_invalid(form)
    def get_context_data(self, **kwargs):
        kwargs["next"] = self.request.GET.get("next")
        kwargs["error"] = self.error
        return super(LoginView, self).get_context_data(**kwargs)

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

# Data Editing Views
@method_decorator(login_required, name="dispatch")
class ListWidgetsView(ListView):
    template_name = "widget_data/list_widgets.html"
    def get_queryset(self):
        return get_editable_widgets_for_user(self.request.user)
    def get_context_data(self, **kwargs):
        kwargs = super(ListWidgetsView, self).get_context_data(**kwargs)
        kwargs["widgets"] = kwargs["object_list"]
        kwargs["uploaders"] = get_uploaders_for_user(self.request.user)
        kwargs["can_edit_users"] = self.request.user.has_perm("auth.add_user")
        kwargs["can_use_admin"] = self.request.user.is_staff
        if not kwargs["widgets"] and not kwargs["uploaders"] and not kwargs["can_edit_users"] and not kwargs["can_use_admin"]:
            raise PermissionDenied("You do not have permission to edit or upload any dashboard data")
        return kwargs

@method_decorator(login_required, name="dispatch")
class ListWidgetParamsView(ListView):
    template_name = "widget_data/list_parametisations.html"
    def get_queryset(self):
        try:
            self.widget = WidgetDefinition.objects.get(family__url=self.kwargs["widget_url"], 
                        label=self.kwargs["label"])
        except WidgetDefinition.DoesNotExist:
            raise Http404("This Widget Definition does not exist")
        if not user_has_edit_permission(self.request.user, self.widget):
            raise PermissionDenied("You do not have permission to edit the data for this widget")
        if not self.widget.parametisation:
            raise PermissionDenied("This widget is not a parametised widget")
        return self.widget.parametisation.keys()
    def get_context_data(self, **kwargs):
        kwargs = super(ListWidgetParamsView, self).get_context_data(**kwargs)
        kwargs["keys"] = kwargs["object_list"]
        pvals = []
        for pval in self.widget.parametisation.parametisationvalue_set.all():
            parameters = pval.parameters()
            pvals.append({
                    "pval": pval,
                    "parameters": [ parameters[k] for k in kwargs["keys"] ],
                    "last_updated": self.widget.data_last_updated(pval=pval),
                    }) 
        kwargs["pvals"] = pvals
        kwargs["widget"] = self.widget
        return kwargs

class WidgetDataForm(forms.Form):
    actual_frequency_display_text=forms.CharField(max_length=60)
    text_block=forms.CharField(widget=forms.Textarea(attrs={"rows": 9, "cols": 50 }), required=False)

def do_common_startup(func):
    def func_out(self, request, *args, **kwargs):
        self.common_startup(request, *args, **kwargs)
        return func(self, request, *args, **kwargs)
    return func_out

class InitialisableFormView(FormView):
    def common_startup(self, request, *args, **kwargs):
       return
    @do_common_startup
    def get(self, request, *args, **kwargs):
        return super(InitialisableFormView, self).get(request, *args, **kwargs)
    @do_common_startup
    def post(self, request, *args, **kwargs):
        return super(InitialisableFormView, self).post(request, *args, **kwargs)
    def get_reset_form(self):
        kwargs = self.get_form_kwargs()
        if "data" in kwargs:
            del kwargs["data"]
        if "files" in kwargs:
            del kwargs["files"]
        return self.get_form_class()(**kwargs)

@method_decorator(login_required, name="dispatch")
class ViewWidgetView(InitialisableFormView):
    template_name = "widget_data/view_widget.html"
    form_class=WidgetDataForm
    def common_startup(self, request, *args, **kwargs):
        try:
            self.widget = WidgetDefinition.objects.get(family__url=kwargs["widget_url"], 
                        label=kwargs["label"])
        except WidgetDefinition.DoesNotExist:
            raise Http404("This Widget Definition does not exist")
        if not user_has_edit_permission(request.user, self.widget):
            raise PermissionDenied("You do not have permission to edit the data for this widget")
        if self.widget.parametisation and not kwargs.get("pval_id"):
            raise Http404("This Widget Definition is parametised")
        if not self.widget.parametisation:
            self.pval = None
        else:
            try:
                self.pval = ParametisationValue.objects.get(pk=pval_id)
            except ParametisationValue.DoesNotExist:
                raise Http404("This parameter value set does not exist")
        return
    def get_stats(self):
        if user_has_edit_all_permission(self.request.user, self.widget):
            statistics = Statistic.objects.filter(tile__widget=self.widget)
        else:
            statistics = Statistic.objects.filter(editable=True,tile__widget=self.widget)
        stats = []
        for s in statistics:
            try:
                data = StatisticData.objects.get(statistic=s, param_value=self.pval)
            except StatisticData.DoesNotExist:
                data = None
            listdata = StatisticListItem.objects.filter(statistic=s, param_value=self.pval)
            stats.append({
                    "statistic": s,
                    "data_last_updated": s.data_last_updated(pval=self.pval),
                    "data": data,
                    "listdata": listdata,
                })
        return stats
    def get_graphs(self):
        graphs = []
        for graph in GraphDefinition.objects.filter(tile__widget=self.widget):
            data = graph.get_data(pval=self.pval)
            graphs.append({
                    "graph": graph,
                    "data_last_updated": graph.data_last_updated(pval=self.pval),
                    "data": data
                    })
        return graphs
    def get_initial(self):
        wd = self.widget.widget_data(pval=self.pval)
        if wd:
            text = wd.text_block
        else:
            text = ""
        return {
                "actual_frequency_display_text": self.widget.actual_frequency_display(wd=wd),
                "text_block": text,
        }
    def get_context_data(self, **kwargs):
        kwargs["pval"] = self.pval
        kwargs["widget"] = self.widget
        kwargs["stats"] = self.get_stats()
        kwargs["graphs"] = self.get_graphs()
        return super(ViewWidgetView, self).get_context_data(**kwargs)
    def form_valid(self, form):
        set_actual_frequency_display_text(self.widget.url(), self.widget.label,
                        form.cleaned_data["actual_frequency_display_text"], pval=self.pval)
        set_text_block(self.widget.url(), self.widget.label,
                    form.cleaned_data["text_block"], pval=self.pval)
        # No redirect on success, so call down to super.form_invalid instead.
        return super(ViewWidgetView, self).form_invalid(form)
 
@method_decorator(login_required, name="dispatch")
class EditStatView(InitialisableFormView):
    template_name = "widget_data/edit_widget.html"
    redirect_out = False
    def get_form_class(self):
        form_class = get_form_class_for_statistic(self.stat)
        if self.stat.is_data_list():
            form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=4)
        return form_class
    def common_startup(self, request, *args, **kwargs):
        try:
            self.stat = get_statistic(kwargs["widget_url"], kwargs["label"], kwargs["stat_url"])
        except LoaderException:
            raise Http404("This Statistic does not exist")
        if not user_has_edit_permission(request.user, self.stat.tile.widget):
            raise PermissionDenied("You do not have permission to edit the data for this widget")
        if not self.stat.editable and not user_has_edit_all_permission(request.user, self.stat.tile.widget):
            raise PermissionDenied("You do not have permission to edit the data for this widget")
        if self.stat.tile.widget.parametisation and not kwargs.get("pval_id"):
            raise Http404("This Widget Definition is parametised")
        if not self.stat.tile.widget.parametisation:
            self.pval = None
        else:
            try:
                self.pval = ParametisationValue.objects.get(pk=kwargs.get("pval_id"))
            except ParametisationValue.DoesNotExist:
                raise Http404("This parameter value set does not exist")
        return 
    def get_success_url(self):
        if self.pval:
            return reverse("view_parametised_widget_data", 
                    kwargs = {
                        "widget_url": self.stat.tile.widget.family.url, 
                        "label": self.stat.tile.widget.label,
                        "pval_id": self.pval.id,
                    })
        else:
            return reverse("view_widget_data", 
                kwargs = {
                    "widget_url": self.stat.tile.widget.family.url, 
                    "label": self.stat.tile.widget.label,
                })
    def get_context_data(self, **kwargs):
        kwargs["pval"] = self.pval
        kwargs["widget"] = self.stat.tile.widget
        kwargs["statistic"] = self.stat
        return super(EditStatView, self).get_context_data(**kwargs)
    def get_initial(self):
        return self.stat.initial_form_data(self.pval)
    def post(self, request, *args, **kwargs):
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            return super(EditStatView, self).post(request, *args, **kwargs)
        self.common_startup(request, *args, **kwargs)
        if request.POST.get("cancel"):
            self.redirect_out=True
        elif not self.stat.is_data_list() and request.POST.get("delete"):
            clear_statistic_data(self.stat)
            self.redirect_out=True
        if self.redirect_out:
            return super(EditStatView, self).form_valid(None)
        else:
            return self.form_invalid(self.get_reset_form())
    def form_valid(self, form):
        if self.stat.is_data_list():
            clear_statistic_list(self.stat, pval=pval)
            for subform in form:
                fd = subform.cleaned_data
                if fd and not fd.get("DELETE"):
                    add_stat_list_item(self.stat, fd["value"], fd["sort_order"], self.pval,
                                fd.get("datetime"), fd.get("level"), fd.get("date"), fd.get("label"),
                                fd.get("traffic_light_code"), fd.get("icon_code"),
                                fd.get("trend"), fd.get("url"))
            if request.POST.get("submit"):
                redirect_out=True
            else:
                form = self.get_reset_form()
        else:
            fd = form.cleaned_data
            set_stat_data(self.stat, fd.get("value"), self.pval,
                            fd.get("traffic_light_code"), fd.get("icon_code"), 
                            fd.get("trend"), fd.get("label"))
            redirect_out=True
        if self.redirect_out:
            return super(EditStatView, self).form_valid(form)
        else:
            return self.form_invalid(form)

def do_common_return(func):
    def func_out(self, request, *args, **kwargs):
        func(self, request, *args, **kwargs)
        return self.common_return(request)
    return func_out

def do_common_wrappers(func):
    return do_common_return(do_common_startup(func))

@method_decorator(login_required, name="dispatch")
class EditGraphView(TemplateResponseMixin, ContextMixin, View):
    template_name = "widget_data/edit_graph.html"
    def common_startup(self, request, *args, **kwargs):
        try:
            self.widget = WidgetDefinition.objects.get(family__url=kwargs["widget_url"], 
                            label=kwargs["label"])
        except WidgetDefinition.DoesNotExist:
            raise Http404("This Widget Definition does not exist")
        if not user_has_edit_permission(request.user, self.widget):
            raise PermissionDenied("You do not have permission to edit the data for this widget")
        try:
            self.graph = GraphDefinition.objects.get(tile__widget=self.widget, tile__url=kwargs["tile_url"])
        except GraphDefinition.DoesNotExist:
            raise Http404("This Graph does not exist")
        if not self.widget.parametisation:
            self.pval = None
        else:
            try:
                self.pval = ParametisationValue.objects.get(pk=kwargs["pval_id"])
            except ParametisationValue.DoesNotExist:
                raise PermissionDenied("This parameter value set does not exist")
        self.form_class = get_form_class_for_graph(self.graph, pval=self.pval)
        self.form_class = forms.formsets.formset_factory(self.form_class, can_delete=True, extra=10)
        self.overrides_form_class = get_override_form_class_for_graph(self.graph)
        if self.graph.dynamic_clusters:
            self.dyncluster_form_class = forms.modelformset_factory(DynamicGraphCluster, form=DynamicGraphClusterForm, can_delete=True, extra=3)
        else:
            self.dyncluster_form_class = None
        self.overrides_form = None
        self.dyncluster_form = None
        self.return_redirect = False
    def reset_forms(self):
        self.form = self.form_class(initial=self.graph.initial_form_data(self.pval))
        if self.overrides_form_class:
            self.overrides_form = self.overrides_form_class(initial=self.graph.initial_override_form_data(self.pval))
        if self.dyncluster_form_class:
            self.dyncluster_form = self.dyncluster_form_class(queryset=self.graph.dynamicgraphcluster_set.filter(param_value=self.pval), 
                                        prefix="clusters", 
                                        form_kwargs={"graph": self.graph, "pval": self.pval})
    @do_common_wrappers
    def get(self, request, *args, **kwargs):
        self.reset_forms()
    def process_subform(self, subform):
        fd = subform.cleaned_data
        if fd and not fd.get("DELETE") and not subform.is_blank(fd):
            gd = GraphData(graph=self.graph, param_value=self.pval)
            gd.value = fd["value"]
            gd.err_valmin = fd.get("err_valmin")
            gd.err_valmax = fd.get("err_valmax")
            if self.graph.use_clusters():
                gd.set_cluster(fd["cluster"])
            gd.dataset = fd["dataset"]
            if self.graph.graph_type == self.graph.LINE:
                if self.graph.horiz_axis_type == self.graph.NUMERIC:
                    gd.horiz_numericval = fd["horiz_value"]
                elif self.graph.horiz_axis_type == self.graph.DATE:
                    gd.horiz_dateval = fd["horiz_value"]
                elif self.graph.horiz_axis_type == self.graph.TIME:
                    gd.horiz_timeval = fd["horiz_value"]
                elif self.graph.horiz_axis_type == self.graph.TIME:
                    gd.horiz_dateval = fd["horiz_value"].date()
                    gd.horiz_timeval = fd["horiz_value"].time()
            gd.save()
    @do_common_wrappers
    def post(self, request, *args, **kwargs):
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            self.form = self.form_class(request.POST)
            if self.overrides_form_class:
                self.overrides_form = self.overrides_form_class(request.POST)
            if self.dyncluster_form_class:
                self.dyncluster_form = self.dyncluster_form_class(request.POST, 
                            queryset=DynamicGraphCluster.objects.filter(graph=self.graph, param_value=self.pval), 
                            prefix="clusters", 
                            form_kwargs={"graph": self.graph, "pval": self.pval})
            if self.form.is_valid() and (not self.overrides_form or self.overrides_form.is_valid()) and (not self.dyncluster_form or self.dyncluster_form.is_valid()):
                clear_graph_data(self.graph, pval=self.pval)
                if self.dyncluster_form:
                    self.dyncluster_form.save()
                for subform in self.form:
                    self.process_subform(subform)
                if self.overrides_form:
                    fod = self.overrides_form.cleaned_data
                    for fldname, fldval in fod.items():
                        ov_type, ov_url = fldname.split("_", 1)
                        set_dataset_override(self.graph, ov_url, fldval, pval=self.pval)
                if request.POST.get("submit"):
                    self.return_redirect=True
                else:
                    self.reset_forms()
        elif request.POST.get("cancel"):
            self.return_redirect=True
    def common_return(self, request):
        if self.return_redirect:
            if self.pval:
                return redirect("view_parametised_widget_data", 
                            widget_url=self.widget.family.url, 
                            label=self.widget.label, pval_id=self.pval.id)
            else: 
                return redirect("view_widget_data", 
                            widget_url=self.widget.family.url, 
                            label=self.widget.label)
        return self.render_to_response(self.get_context_data())
    def get_context_data(self, **kwargs):
        kwargs["widget"] =  self.widget
        kwargs["pval"] = self.pval
        kwargs["graph"] =  self.graph
        kwargs["form"] = self.form
        kwargs["overrides_form"] = self.overrides_form
        kwargs["dyncluster_form"] = self.dyncluster_form
        return super(EditGraphView, self).get_context_data(**kwargs)

class UploadForm(forms.Form):
    new_actual_frequency_display_value=forms.CharField(max_length=60, required=False)
    file=forms.FileField()
        
@method_decorator(login_required, name="dispatch")
class UploadView(InitialisableFormView):
    template_name = "widget_data/upload_data.html"
    form_class    = UploadForm
    def common_startup(self, request, *args, **kwargs):
        try:
            self.uploader = Uploader.objects.get(app=kwargs["uploader_app"])
        except Uploader.DoesNotExist:
            raise Http404("This uploader does not exist")
        if not user_has_uploader_permission(request.user, self.uploader):
            raise PermissionDenied("You do not have permission to upload data for this uploader")
        self.fmt = get_update_format(kwargs["uploader_app"])
        self.messages = []
    def form_valid(self, form):
        self.messages = self.handle_uploaded_file(form.cleaned_data["new_actual_frequency_display_value"])
        return self.form_invalid(self.get_reset_form())
    def get_context_data(self, **kwargs):
        kwargs["uploader"] = self.uploader
        kwargs["format"] = self.fmt
        kwargs["num_sheets"] = len(self.fmt["sheets"])
        kwargs["messages"] = self.messages
        return super(UploadView, self).get_context_data(**kwargs)
    def handle_uploaded_file(self, freq_display=None):
        try:
            return do_upload(self.uploader, self.request.FILES["file"], 
                        actual_freq_display=freq_display, verbosity=3)
        except LoaderException, e:
            return [ "Upload Error: %s" % unicode(e) ]

def handle_uploaded_file(uploader, uploaded_file, freq_display=None):
    try:
        return do_upload(uploader, uploaded_file, 
                    actual_freq_display=freq_display, verbosity=3)
    except LoaderException, e:
        return [ "Upload Error: %s" % unicode(e) ]

@login_required
@permission_required('auth.add_user', raise_exception=True)
def maintain_users(request):
    return render(request, "users/list_users.html", {"users": User.objects.all()})

class AddUserForm(forms.Form):
    PASSWD_AUTO = "2"
    PASSWD_MANUAL = "3"
    username=forms.CharField(max_length=30, required=True)
    first_name=forms.CharField(max_length=30, required=False)
    last_name=forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    groups = forms.ModelMultipleChoiceField(required=False, 
                        queryset=Group.objects.all().order_by("name"),
                        widget=forms.CheckboxSelectMultiple())
    mode_password = forms.ChoiceField(
            required=True,
            choices=[
                    ( PASSWD_AUTO, "Generate password automatically and email" ),
                    ( PASSWD_MANUAL, "Manually set password" ),
            ],
            initial = PASSWD_AUTO,
            widget=forms.RadioSelect(attrs={
                    'onclick': "showHidePasswordFieldsFromRadioButton('mode_password')",
                })
            )
    password1 = forms.CharField(max_length=64, required=False, 
            label="Password",
            widget=forms.widgets.PasswordInput)
    password2 = forms.CharField(max_length=64, required=False, 
            label="Confirm Password",
            widget=forms.widgets.PasswordInput)
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError("This username is already in use")
        except User.DoesNotExist:
            return username
    def clean(self):
        data = super(AddUserForm, self).clean()
        if self.data["mode_password"] == self.PASSWD_AUTO:
            self.add_error("mode_password", "Automatic password generation not supported yet")
        elif self.data["mode_password"] == self.PASSWD_MANUAL:
            if not self.data["password1"]:
                self.add_error("password1", "Please enter new password")
            elif not self.data["password2"]:
                self.add_error("password2", "Please confirm new password")
            elif self.data["password1"] != self.data["password2"]:
                self.add_error("password2", "Passwords do not match")
        return data

@method_decorator([ 
                    login_required, 
                    permission_required('auth.add_user', raise_exception=True) 
            ], name="dispatch")
class AddUserView(FormView):
    template_name = "users/add_user.html"
    success_url = reverse_lazy('maintain_users')
    form_class=AddUserForm
    def post(self, request, *args, **kwargs):
        if request.POST.get("cancel"):
            return HttpResponseRedirect(self.get_success_url())
        return super(AddUserView, self).post(request, *args, **kwargs)
    def form_valid(self, form):
        data = form.cleaned_data
        user = User()
        user.username = data["username"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.is_active = bool(data.get("is_active"))
        if data["mode_password"] == AddUserForm.PASSWD_MANUAL:
            user.set_password(data["password1"])
        user.save()
        for grp in data["groups"]:
            user.groups.add(grp)
        return super(AddUserView, self).form_valid(form)

class EditUserForm(forms.Form):
    PASSWD_UNCHANGED = "1"
    PASSWD_AUTO_RESET = "2"
    PASSWD_MANUAL_RESET = "3"
    first_name=forms.CharField(max_length=30, required=False)
    last_name=forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    is_active = forms.BooleanField(required=False)
    groups = forms.ModelMultipleChoiceField(required=False,
                        queryset=Group.objects.all().order_by("name"),
                        widget=forms.CheckboxSelectMultiple())
    mode_password = forms.ChoiceField(
            required=True,
            choices=[
                    ( PASSWD_UNCHANGED, "Leave password unchanged" ),
                    ( PASSWD_AUTO_RESET, "Reset password and email" ),
                    ( PASSWD_MANUAL_RESET, "Manually set password" ),
            ],
            initial = PASSWD_UNCHANGED,
            widget=forms.RadioSelect(attrs={
                    'onclick': "showHidePasswordFieldsFromRadioButton('mode_password')",
                })
            )
    password1 = forms.CharField(max_length=64, required=False, 
            label="Password",
            widget=forms.widgets.PasswordInput)
    password2 = forms.CharField(max_length=64, required=False, 
            label="Confirm Password",
            widget=forms.widgets.PasswordInput)
    def __init__(self, *args, **kwargs):
        init = kwargs.get("initial")
        if isinstance(init, User):
           initial = {
               'first_name': init.first_name,
               'last_name': init.last_name,
               'email': init.email,
               'is_active': init.is_active,
               'groups': [ g.id for g in init.groups.all() ],
           }
           kwargs["initial"] = initial
        super(EditUserForm,self).__init__(*args, **kwargs)
    def clean(self):
        data = super(EditUserForm, self).clean()
        if self.data["mode_password"] == self.PASSWD_AUTO_RESET:
            self.add_error("mode_password", "Automatic password reset not supported yet")
        elif self.data["mode_password"] == self.PASSWD_MANUAL_RESET:
            if not self.data["password1"]:
                self.add_error("password1", "Please enter new password")
            elif not self.data["password2"]:
                self.add_error("password2", "Please confirm new password")
            elif self.data["password1"] != self.data["password2"]:
                self.add_error("password2", "Passwords do not match")
        return data

@method_decorator([ 
                    login_required, 
                    permission_required('auth.add_user', raise_exception=True) 
            ], name="dispatch")
class EditUserView(InitialisableFormView):
    template_name = "users/edit_user.html"
    success_url = reverse_lazy('maintain_users')
    form_class=EditUserForm
    def common_startup(self, request, username, *args, **kwargs):
        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404("User does not exist")
    def get_initial(self):
        return self.user
    def get_context_data(self, **kwargs):
        kwargs["u"] = self.user
        return super(EditUserView, self).get_context_data(**kwargs)
    def post(self, request, *args, **kwargs):
        if request.POST.get("cancel"):
            return HttpResponseRedirect(self.get_success_url())
        return super(EditUserView, self).post(request, *args, **kwargs)
    def form_valid(self, form):
        data = form.cleaned_data
        self.user.first_name = data["first_name"]
        self.user.last_name = data["last_name"]
        self.user.email = data["email"]
        self.user.is_active = bool(data.get("is_active"))
        self.user.save()
        self.user.groups.clear()
        for grp in data["groups"]:
            self.user.groups.add(grp)
        if data["mode_password"] == EditUserForm.PASSWD_MANUAL_RESET:
            self.user.set_password(data["password1"])
            self.user.save()
        return super(EditUserView, self).form_valid(form)

@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_action(request, username, action):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseForbidden("User does not exist")
    if action == "deactivate":
        user.is_active = False
        user.save()
    elif action == "activate":
        user.is_active = True
        user.save()
    elif action == "delete":
        if user.is_active:
            return HttpResponseForbidden("Cannot delete an active user")
        user.delete()
    else:
        return HttpResponseForbidden("Action %s not supported" % action)
    return redirect("maintain_users")

