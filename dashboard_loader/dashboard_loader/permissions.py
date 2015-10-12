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

from widget_def.models import WidgetDefinition
from dashboard_loader.models import Uploader

# Permission methods

def get_editable_widgets_for_user(user):
    widgets = []
    for w in WidgetDefinition.objects.all():
        if user.has_perm(w.family.edit_permission_label()) or user.has_perm(w.family.edit_all_permission_label()):
            widgets.append(w)
    return widgets

def user_has_edit_permission(user, widget):
    return user.has_perm(widget.family.edit_permission_label()) or user.has_perm(widget.family.edit_all_permission_label())

def user_has_edit_all_permission(user, widget):
    return user.has_perm(widget.family.edit_all_permission_label())

def get_uploaders_for_user(user):
    uploaders = []
    for u in Uploader.objects.all():
        if user.has_perm(u.permission_label()):
            uploaders.append(u)
    return uploaders

def user_has_uploader_permission(user, uploader):
    return user.has_perm(uploader.permission_label())

