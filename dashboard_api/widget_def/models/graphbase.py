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


from django.db import models
from widget_def.parametisation import parametise_label
from widget_def.model_json_tools import *

class GraphClusterBase(models.Model):
    """
    Abstract base class for graph clusters.  Graph clusters may be statically defined (in widget_def)
    or dynamically defined (in widget_data), thus a common abstract base class is required.
    """
    api_state_def = {
        "label": JSON_ATTR(attribute="url"),
        "name": JSON_ATTR(attribute="label", parametise=True),
        "hyperlink": JSON_ATTR(parametise=True)
    }
    # Histo/bar clusters or Pies
    graph=models.ForeignKey("widget_def.GraphDefinition", help_text="The graph the cluster belongs to")
    url=models.SlugField(verbose_name="label", help_text="A short symbolic label for the cluster, as used in the API")
    label=models.CharField(verbose_name="name", max_length=80, help_text="A longer descriptive name for the cluster, suitable for presentation to an end user.")
    hyperlink=models.URLField(blank=True, null=True, help_text="An optional external URL to link for this cluster ")
    sort_order=models.IntegerField(help_text="How to sort the cluster within the graph")
    def widget(self):
        return self.graph.tile.widget
    def __unicode__(self):
        return self.url
    class Meta:
        abstract=True
        unique_together = [("graph", "sort_order"), ("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "sort_order" ]
    def __getstate__(self, view=None):
        return {
            "label": self.url,
            "name": parametise_label(self.widget(), view, self.label),
            "hyperlink": parametise_label(self.widget(), view, self.hyperlink),
        }


