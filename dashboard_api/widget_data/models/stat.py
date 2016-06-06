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

from decimal import Decimal, ROUND_HALF_UP

from django.db import models

# Create your models here.

class StatisticData(models.Model):
    statistic = models.ForeignKey("widget_def.Statistic")
    param_value = models.ForeignKey("widget_def.ParameterValue", blank=True, null=True)
    label=models.CharField(max_length=80, blank=True, null=True)
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    traffic_light_code = models.ForeignKey("widget_def.TrafficLightScaleCode", blank=True, null=True)
    icon_code = models.ForeignKey("widget_def.IconCode", blank=True, null=True)
    trend = models.SmallIntegerField(choices=(
                    (1, "Upwards"),
                    (0, "Steady"),
                    (-1, "Downwards"),
                ), blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together=[
                    ("statistic", "param_value"),
        ]
    def display_val(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return unicode(self.intval)
            else:
                if self.decval is None:
                    return None
                else:
                    return unicode(self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP))
        else:
            return self.strval
    def value(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return self.intval
            else:
                if self.decval is None:
                    return None
                else:
                    return self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP)
        else:
            return self.strval
    def __unicode__(self):
        if self.param_value:
            return "<Data for %s (%s)>" % unicode(self.statistic, repr(self.param_value.parameters()))
        else:
            return "<Data for %s>" % unicode(self.statistic)

