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

import datetime
import pytz

from django.conf import settings
from django.db import models

# Create your models here.
tz = pytz.timezone(settings.TIME_ZONE)

class GraphDataQuerySet(models.QuerySet):
    def natural_order(self, graph):
        # args = ["graph", "cluster", "dataset"]
        args = ["graph", ]
        if graph.use_clusters():
            args.append("cluster")
        args.append("dataset")
        if graph.horiz_axis_type == graph.NUMERIC:
            args.append("horiz_numericval")
        elif graph.horiz_axis_type == graph.DATE:
            args.append("horiz_dateval")
        elif graph.horiz_axis_type == graph.TIME:
            args.append("horiz_timeval")
        elif graph.horiz_axis_type == graph.DATETIME:
            args.append("horiz_dateval")
            args.append("horiz_timeval")
        if graph.use_numeric_axes:
            args.append("value")
        return self.order_by(*args)
    natural_order.queryset_only = True

class GraphData(models.Model):
    graph = models.ForeignKey("widget_def.GraphDefinition")
    cluster = models.ForeignKey("widget_def.GraphCluster", blank=True, null=True)
    dataset = models.ForeignKey("widget_def.GraphDataset", blank=True, null=True)
    value = models.DecimalField(max_digits=14, decimal_places=4,
                        blank=True, null=True)
    horiz_numericval = models.DecimalField(max_digits=14, decimal_places=4,
                        blank=True, null=True)
    horiz_dateval = models.DateField(blank=True, null=True)
    horiz_timeval = models.TimeField(blank=True, null=True)
    objects = GraphDataQuerySet.as_manager()
    last_updated = models.DateTimeField(auto_now=True)
    def horiz_value(self):
        if self.graph.horiz_axis_type == self.graph.NUMERIC:
            return self.horiz_numericval
        elif self.graph.horiz_axis_type == self.graph.DATE:
            return self.horiz_dateval
        elif self.graph.horiz_axis_type == self.graph.TIME:
            return self.horiz_timeval
        elif self.graph.horiz_axis_type == self.graph.DATETIME:
            return tz.localize(datetime.datetime.combine(self.horiz_dateval,self.horiz_timeval))
        else:
            return None
    def horiz_json_value(self):
        return self.graph.jsonise_horiz_value(self.horiz_value())
    class Meta:
        ordering = ("graph", "cluster", "dataset", "horiz_numericval", "horiz_dateval", "horiz_timeval")

