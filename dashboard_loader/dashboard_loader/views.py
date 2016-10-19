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
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
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

@login_required
def view_widget(request, widget_url, label, pval_id=None):
    try:
        w = WidgetDefinition.objects.get(family__url=widget_url, 
                    label=label)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    if w.parametisation and not pval_id:
        return HttpResponseNotFound("This Widget Definition is parametised")
    if not w.parametisation:
        pval = None
    else:
        try:
            pval = ParametisationValue.objects.get(pk=pval_id)
        except ParametisationValue.DoesNotExist:
            return HttpResponseNotFound("This parameter value set does not exist")
    edit_all = user_has_edit_all_permission(request.user, w)
    if edit_all:
        statistics = Statistic.objects.filter(tile__widget=w)
    else:
        statistics = Statistic.objects.filter(editable=True,tile__widget=w)
    stats = []
    for s in statistics:
        try:
            data = StatisticData.objects.get(statistic=s, param_value=pval)
        except StatisticData.DoesNotExist:
            data = None
        listdata = StatisticListItem.objects.filter(statistic=s, param_value=pval)
        stats.append({
                "statistic": s,
                "data_last_updated": s.data_last_updated(pval=pval),
                "data": data,
                "listdata": listdata,
            })
    graphs = []
    for graph in GraphDefinition.objects.filter(tile__widget=w):
        data = graph.get_data(pval=pval)
        graphs.append({
                "graph": graph,
                "data_last_updated": graph.data_last_updated(pval=pval),
                "data": data
                })
    if request.method == "POST":
        form = WidgetDataForm(request.POST)
        if form.is_valid():
            set_actual_frequency_display_text(w.url(), w.label,
                        form.cleaned_data["actual_frequency_display_text"], pval=pval)
            set_text_block(w.url(), w.label,
                        form.cleaned_data["text_block"], pval=pval)
    else:
        wd = w.widget_data(pval=pval)
        if wd:
            text = wd.text_block
        else:
            text = ""
        form = WidgetDataForm(initial={
                "actual_frequency_display_text": w.actual_frequency_display(wd=wd),
                "text_block": text,
                })
    return render(request, "widget_data/view_widget.html", {
            "pval": pval,
            "widget": w,
            "stats": stats,
            "graphs": graphs,
            "form": form,
            })

@login_required
def edit_stat(request, widget_url, label, stat_url, pval_id=None):
    try:
        s = get_statistic(widget_url, label, stat_url)
    except LoaderException:
        return HttpResponseNotFound("This Statistic does not exist")
    if not user_has_edit_permission(request.user, s.tile.widget):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    if not s.editable and not user_has_edit_all_permission(request.user, s.tile.widget):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    if s.tile.widget.parametisation and not pval_id:
        return HttpResponseNotFound("This Widget Definition is parametised")
    if not s.tile.widget.parametisation:
        pval = None
    else:
        try:
            pval = ParametisationValue.objects.get(pk=pval_id)
        except ParametisationValue.DoesNotExist:
            return HttpResponseNotFound("This parameter value set does not exist")
    form_class = get_form_class_for_statistic(s)
    if s.is_data_list():
        form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=4)
    redirect_out = False
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if form.is_valid():
                if s.is_data_list():
                    clear_statistic_list(s, pval=pval)
                    for subform in form:
                        fd = subform.cleaned_data
                        if fd and not fd.get("DELETE"):
                            add_stat_list_item(s, fd["value"], fd["sort_order"], pval,
                                        fd.get("datetime"), fd.get("level"), fd.get("date"), fd.get("label"),
                                        fd.get("traffic_light_code"), fd.get("icon_code"),
                                        fd.get("trend"), fd.get("url"))
                    if request.POST.get("submit"):
                        redirect_out=True
                    else:
                        form = form_class(initial=s.initial_form_data(pval))
                else:
                    fd = form.cleaned_data
                    set_stat_data(s, fd.get("value"), pval,
                                    fd.get("traffic_light_code"), fd.get("icon_code"), 
                                    fd.get("trend"), fd.get("label"))
                    redirect_out=True
        elif request.POST.get("cancel"):
            redirect_out=True
        elif not s.is_data_list() and request.POST.get("delete"):
            clear_statistic_data(s)
            redirect_out=True
        else:
            form = form_class(initial=s.initial_form_data(pval))
    else:
        form = form_class(initial=s.initial_form_data(pval))

    if redirect_out:
        if pval:
            return redirect("view_parametised_widget_data", 
                    widget_url=s.tile.widget.family.url, 
                    label=s.tile.widget.label,
                    pval_id=pval_id)
        else:
            return redirect("view_widget_data", 
                widget_url=s.tile.widget.family.url, 
                label=s.tile.widget.label)

    return render(request, "widget_data/edit_widget.html", {
                "pval": pval,
                "widget": s.tile.widget,
                "statistic": s,
                "form": form
                })

@login_required
def edit_graph(request, widget_url, label, tile_url, pval_id=None):
    try:
        w = WidgetDefinition.objects.get(family__url=widget_url, 
                        label=label)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    try:
        g = GraphDefinition.objects.get(tile__widget=w, tile__url=tile_url)
    except GraphDefinition.DoesNotExist:
        return HttpResponseNotFound("This Graph does not exist")
    if not g.widget().parametisation:
        pval = None
    else:
        try:
            pval = ParametisationValue.objects.get(pk=pval_id)
        except ParametisationValue.DoesNotExist:
            return HttpResponseNotFound("This parameter value set does not exist")

    form_class = get_form_class_for_graph(g, pval=pval)
    form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=10)
    overrides_form_class = get_override_form_class_for_graph(g)
    overrides_form = None
    if g.dynamic_clusters:
        dyncluster_form_class = forms.modelformset_factory(DynamicGraphCluster, form=DynamicGraphClusterForm, can_delete=True, extra=3)
    else:
        dyncluster_form_class = None
    dyncluster_form = None
    return_redirect = False
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if overrides_form_class:
                overrides_form = overrides_form_class(request.POST)
            if dyncluster_form_class:
                dyncluster_form = dyncluster_form_class(request.POST, queryset=DynamicGraphCluster.objects.filter(graph=g, param_value=pval), prefix="clusters", form_kwargs={"graph": g, "pval": pval})
            if form.is_valid() and (not overrides_form or overrides_form.is_valid()) and (not dyncluster_form or dyncluster_form.is_valid()):
                clear_graph_data(g, pval=pval)
                if dyncluster_form:
                    dyncluster_form.save()
                for subform in form:
                    fd = subform.cleaned_data
                    if fd and not fd.get("DELETE"):
                        gd = GraphData(graph=g, param_value=pval)
                        gd.value = fd["value"]
                        gd.err_valmin = fd.get("err_valmin")
                        gd.err_valmax = fd.get("err_valmax")
                        if g.use_clusters():
                            gd.set_cluster(fd["cluster"])
                        gd.dataset = fd["dataset"]
                        if g.graph_type == g.LINE:
                            if g.horiz_axis_type == g.NUMERIC:
                                gd.horiz_numericval = fd["horiz_value"]
                            elif g.horiz_axis_type == g.DATE:
                                gd.horiz_dateval = fd["horiz_value"]
                            elif g.horiz_axis_type == g.TIME:
                                gd.horiz_timeval = fd["horiz_value"]
                            elif g.horiz_axis_type == g.TIME:
                                gd.horiz_dateval = fd["horiz_value"].date()
                                gd.horiz_timeval = fd["horiz_value"].time()
                        gd.save()
                if overrides_form:
                    fod = overrides_form.cleaned_data
                    for fldname, fldval in fod.items():
                        ov_type, ov_url = fldname.split("_", 1)
                        if ov_type == 'cluster':
                            set_cluster_override(g, ov_url, fldval, pval=pval)
                        else:
                            set_dataset_override(g, ov_url, fldval, pval=pval)
                if request.POST.get("submit"):
                    return_redirect=True
                else:
                    form = form_class(initial=g.initial_form_data(pval))
                    if overrides_form_class:
                        overrides_form = overrides_form_class(initial=g.initial_override_form_data(pval))
                    if dyncluster_form_class:
                        dyncluster_form = dyncluster_form_class(queryset=g.dynamicgraphcluster_set.filter(param_value=pval), prefix="clusters", form_kwargs={"graph": g, "pval": pval})
        elif request.POST.get("cancel"):
            return_redirect=True
        else:
            form = form_class(initial=g.initial_form_data(pval))
            if overrides_form_class:
                overrides_form = overrides_form_class(initial=g.initial_override_form_data(pval))
            if dyncluster_form_class:
                dyncluster_form = dyncluster_form_class(queryset=g.dynamicgraphcluster_set.filter(param_value=pval), prefix="clusters", form_kwargs={"graph": g, "pval": pval})
    else:
        form = form_class(initial=g.initial_form_data(pval))
        if overrides_form_class:
            overrides_form = overrides_form_class(initial=g.initial_override_form_data(pval))
        if dyncluster_form_class:
            dyncluster_form = dyncluster_form_class(queryset=g.dynamicgraphcluster_set.filter(param_value=pval), prefix="clusters", form_kwargs={"graph": g, "pval": pval})
    if return_redirect:
        if pval:
            return redirect("view_parametised_widget_data", 
                        widget_url=w.family.url, 
                        label=label, pval_id=pval_id)
        else: 
            return redirect("view_widget_data", 
                        widget_url=w.family.url, 
                        label=label)
    return render(request, "widget_data/edit_graph.html", {
                "widget": w,
                "pval": pval,
                "graph": g,
                "form": form,
                "overrides_form": overrides_form,
                "dyncluster_form": dyncluster_form,
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
class EditUserView(FormView):
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
    def get(self, request, *args, **kwargs):
        self.common_startup(request, *args, **kwargs)
        return super(EditUserView, self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        if request.POST.get("cancel"):
            return HttpResponseRedirect(self.get_success_url())
        self.common_startup(request, *args, **kwargs)
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

