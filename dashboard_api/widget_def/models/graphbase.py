#   Copyright 2015,2016 Data61
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


class GraphClusterBase(models.Model):
    # Histo/bar clusters or Pies
    graph=models.ForeignKey("widget_def.GraphDefinition")
    url=models.SlugField(verbose_name="label")
    label=models.CharField(verbose_name="name", max_length=80)
    hyperlink=models.URLField(blank=True, null=True)
    sort_order=models.IntegerField()
    def __unicode__(self):
        return self.url
    class Meta:
        abstract=True
        unique_together = [("graph", "sort_order"), ("graph", "url"), ("graph", "label")]
        ordering = [ "graph", "sort_order" ]
    def __getstate__(self, view=None):
        return {
            "label": self.url,
            "name": parametise_label(self.graph.tile.widget, view, self.label),
            "hyperlink": parametise_label(self.graph.tile.widget, view, self.hyperlink),
        }


