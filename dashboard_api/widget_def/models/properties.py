#   Copyright 2017 CSIRO
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

from django.db import models
from widget_def.model_json_tools import *

# Create your models here.

class PropertyGroup(models.Model, WidgetDefJsonMixin):
    """
    A Property Group is a family of related properties.
    It can be thought of as a dictionary of server-stored values. The interpretation of properties
    and property groups is implementation-specific.
    """
    export_def = {
        "name": JSON_ATTR(),
        "label": JSON_ATTR(),
        "properties": JSON_RECURSEDOWN("Property", "properties", "group", "key", app="widget_def")
    }
    export_lookup = { "name": "name" }
    api_state_def = {
        "name": JSON_ATTR(),
        "label": JSON_ATTR(),
        "properties": JSON_RECURSEDICT("properties", "key", "value")
    }
    name = models.CharField(max_length=80, help_text="Descriptive name of the Property Group", unique=True)
    label = models.SlugField(help_text="Short symbolic name of the Property Group, as used in API", unique=True)
    @classmethod
    def import_data(cls, data):
        if data.get("type"):
            output = []
            for pg in data["exports"]:
                output.append(cls.import_data(pg))
            return output
        return super(PropertyGroup, cls).import_data(data)
    def __unicode__(self):
        return "%s[%s]" % (self.name, self.label)
    def getindex(self):
        return {
            "name": self.name,
            "label": self.label,
        }

class Property(models.Model, WidgetDefJsonMixin):
    export_def = {
        "group": JSON_INHERITED(related_name="properties"),
        "key": JSON_ATTR(),
        "value": JSON_ATTR(),
    }
    export_lookup = { "group": "group", "key": "key" }
    group = models.ForeignKey(PropertyGroup, related_name="properties", help_text="The group this property belongs to")
    key = models.CharField(max_length=255, help_text="The key (lookup value) of this property")
    value = models.CharField(max_length=1024, help_text="The value (mapped value) of this property")
    def __unicode__(self):
        return '(%s) "%s": "%s"' % (self.group.label, self.key, self.value)
    class Meta:
        unique_together = [ ('group', 'key'), ]
        ordering = [ 'group', 'key' ]
        verbose_name_plural = "properties"

