from widget_def.models import WidgetDefinition

# Permission methods

def get_editable_widgets_for_user(user):
    # TODO: Check permissions
    return WidgetDefinition.objects.all()

def user_has_edit_permission(user, widget):
    # TODO: Check permissions
    return True

