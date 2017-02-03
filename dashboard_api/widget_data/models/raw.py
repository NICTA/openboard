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
from widget_def.view_tools import csv_escape

# Create your models here.

class RawDataRecord(models.Model):
    rds = models.ForeignKey("widget_def.RawDataSet")
    param_value = models.ForeignKey("widget_def.ParametisationValue", blank=True, null=True)
    sort_order = models.IntegerField()
    csv = models.TextField(null=True)
    def update_csv(self):
        out = ""
        first_cell = True
        for col in self.rds.rawdatasetcolumn_set.all():
            if not first_cell:
                out += ","
            try:
                rd = self.rawdata_set.get(column=col)
                out += rd.csv()
            except RawData.DoesNotExist:
                pass
            first_cell = False
        out += "\n"
        self.csv = out
        self.save()
    def json(self):
        result = {}
        for col in self.rds.rawdatasetcolumn_set.all():
            try:
                rd = self.rawdata_set.get(column=col)
                result[col.url] = rd.json_val()
            except RawData.DoesNotExist:
                result[col.url] = None
        return result
    class Meta:
        unique_together= [ ("rds", "param_value", "sort_order"), ]
        ordering = ("rds", "param_value", "sort_order")

class RawData(models.Model):
    record = models.ForeignKey(RawDataRecord)
    column = models.ForeignKey("widget_def.RawDataSetColumn")
    value = models.CharField(max_length=1024, blank=True)
    def csv(self):
        return csv_escape(self.value)
    def json_val(self):
        try:
            return int(self.value)
        except Exception, e:
            pass
        try:
            return float(self.value)
        except Exception, e:
            pass
        return self.value
    class Meta:
        unique_together=("record", "column")
        ordering = ("record", "column")

