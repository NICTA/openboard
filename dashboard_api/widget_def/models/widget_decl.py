#   Copyright 2015,2016,2017 CSIRO
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

import json

from django.db import models

from widget_def.models.views import WidgetView
from widget_def.model_json_tools import *

# Create your models here.

class ViewWidgetDeclaration(models.Model, WidgetDefJsonMixin):
    """
    Declares that a given :model:`widget_def.WidgetDefinition` should be included in 
    a given :model:`widget_def.WidgetView`
    """
    export_def = {
        "definition": JSON_INHERITED("views"),
        "view": JSON_CAT_LOOKUP(["view", "label"], lambda js, key, imp_kwargs: WidgetView.objects.get(label=js["view"])),
        "sort_order": JSON_IMPLIED(),
        "child_view": JSON_CAT_LOOKUP(["child_view","label"], lambda js, key, imp_kwargs: WidgetView.objects.get(label=js["child_view"]), optional=True),
        "child_view_text": JSON_ATTR(deciders=["child_view", "child_view_text"])
    }
    export_lookup = { "definition": "definition", "view": "view" }
    api_state_def = {
        "definition": JSON_PASSDOWN(solo=True, extend={
                "current_view": JSON_CAT_LOOKUP(["view", "label"], None),
                "child_view": JSON_CAT_LOOKUP(["child_view","label"], None, optional=True),
                "child_view_text": JSON_ATTR(deciders=["child_view", "child_view_text"])
        })
    }
    definition = models.ForeignKey("WidgetDefinition", related_name="views", help_text="The WidgetDefinition to include in the WidgetView")
    view = models.ForeignKey(WidgetView, limit_choices_to={'external_url': None}, related_name="widgets", help_text="The WidgetView the WidgetDefinition is to be included in")
    sort_order = models.IntegerField(help_text="How the widget is to be sorted within the view")
    child_view = models.ForeignKey(WidgetView, null=True, blank=True, related_name="declarations", help_text="(Optional) The label of a view which can be navigated to through this widget.  Would typically be a child view of the containing view, or at least in the same navigation hierarchy, but this is not required.")
    child_view_text = models.CharField(max_length=255, null=True, blank=True, help_text="The text to display in the hyperlink pointing to the child view.")
    state_cache = models.TextField(help_text="Cached widget json description - populated automatically, do not edit by hand.")
    def __unicode__(self):
        return "%s (%s)" % (self.definition.family.name, self.view.name)
    class Meta:
        unique_together=[("definition", "view"), ("view", "sort_order")]
        ordering = ("view", "sort_order")
    def __getstate__(self):
        return json.loads(self.state_cache)
    def update_state_cache(self, *args, **kwargs):
        self.state_cache=json.dumps(super(ViewWidgetDeclaration, self).__getstate__(view=self.view))
        super(ViewWidgetDeclaration, self).save(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.update_state_cache(*args, **kwargs)

