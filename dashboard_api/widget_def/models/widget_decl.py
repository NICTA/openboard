#   Copyright 2015,2016 NICTA
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

from widget_def.models.reference import WidgetView, Theme, Location, Frequency
from widget_def.models.widget_definition import WidgetDefinition

# Create your models here.

# Old Widget Declarations (deprecated)

class WidgetDeclaration(models.Model):
    definition = models.ForeignKey(WidgetDefinition)
    theme = models.ForeignKey(Theme)
    frequency = models.ForeignKey(Frequency, limit_choices_to={
                            "display_mode": True
                    })
    location = models.ForeignKey(Location)
    def __unicode__(self):
        return "%s (%s:%s:%s)" % (self.definition.family.name, self.theme.name, self.location.name, self.frequency.name)
    def __getstate__(self):
        return self.definition.__getstate__()
    def export(self):
        return {
            "theme": self.theme.url,
            "frequency": self.frequency.url,
            "location": self.location.url,
        }
    @classmethod
    def import_data(cls, definition, data):
        try:
            decl = WidgetDeclaration.objects.get(definition=definition, 
                            location__url=data["location"],
                            frequency__url=data["frequency"],
                            theme__url=data["theme"])
        except WidgetDeclaration.DoesNotExist:
            decl = WidgetDeclaration(definition=definition)
            decl.location = Location.objects.get(url=data["location"])
            decl.frequency = Frequency.objects.get(url=data["frequency"])
            decl.theme = Theme.objects.get(url=data["theme"])
            decl.save()
        return decl
    class Meta:
        unique_together = ( ("theme", "location", "frequency", "definition"),)
        ordering = ("theme", "location", "frequency", "definition")

class ViewWidgetDeclaration(models.Model):
    definition = models.ForeignKey(WidgetDefinition)
    view = models.ForeignKey(WidgetView, related_name="widgets")
    sort_order = models.IntegerField()
    child_view = models.ForeignKey(WidgetView, null=True, blank=True, related_name="declarations")
    child_view_text = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return "%s (%s)" % (self.definition.family.name, self.view.name)
    class Meta:
        unique_together=[("definition", "view"), ("view", "sort_order")]
        ordering = ("view", "sort_order")
    def __getstate__(self):
        wstate = self.definition.__getstate__()
        if self.child_view:
            wstate["child_view"] = self.child_view.label
            if self.child_view_text:
                wstate["child_view"] = self.child_view_text
        return wstate
    def export(self):
        data = {
            "view": self.view.label,
            "sort_order": self.sort_order,
        } 
        if self.child_view:
            data["child_view"] = self.child_view.label
            if self.child_view_text:
                data["child_view_text"] = self.child_view_text
        return data
    @classmethod
    def import_data(cls, definition, data):
        try:
            decl = ViewWidgetDeclaration.objects.get(definition=definition,
                                view__label=data["view"])
        except ViewWidgetDeclaration.DoesNotExist:
            decl = ViewWidgetDeclaration(definition=definition,
                            view = WidgetView.objects.get(label=data["view"]))
        decl.sort_order = data["sort_order"]
        if "child_view" in data:
            decl.child_view = WidgetView.objects.get(label=data["child_view"])
        decl.child_view_text = data.get("child_view_text")
        decl.save()
        return decl

