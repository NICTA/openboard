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


