from widget_def.models import WidgetDefinition

# Permission methods

def get_editable_widgets_for_user(user):
    # TODO: Check permissions
    widgets = []
    for w in WidgetDefinition.objects.all():
        if user.has_perm(w.family.edit_permission_label()) or user.has_perm(w.family.edit_permission_label()):
            widgets.append(w)
    return widgets

def user_has_edit_permission(user, widget):
    return user.has_perm(widget.family.edit_permission_label()) or user.has_perm(widget.family.edit_all_permission_label())

def user_has_edit_all_permission(user, widget):
    return user.has_perm(widget.family.edit_all_permission_label())

