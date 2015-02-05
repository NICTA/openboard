from django import template
from django.conf import settings

register = template.Library()

class SettingsNode(template.Node):
    def __init__(self, setting_item):
        self.setting_item = setting_item
    def render(self, context):
        return getattr(settings, self.setting_item)

@register.tag(name="settings")
def do_settings(parser, token):
    try:
        tag_name, setting_item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return SettingsNode(setting_item)


