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

from django.db import models

from widget_def.models.widget_definition import WidgetDefinition

class RawDataSet(models.Model):
    widget = models.ForeignKey(WidgetDefinition)
    url = models.SlugField()
    filename = models.CharField(max_length=128)
    def __unicode__(self):
        return "%s.%s (%s)" % (self.widget.family.url, self.url, self.filename)
    def export(self):
        return {
            "url": self.url,
            "filename": self.filename,
            "columns": [ c.export() for c in self.rawdatasetcolumn_set.all() ],
        }
    @classmethod
    def import_data(cls, widget, data):
        try:
            rds = RawDataSet.objects.get(widget=widget, url=data["url"])
        except RawDataSet.DoesNotExist:
            rds = RawDataSet(widget=widget, url=data["url"])
        rds.filename = data["filename"]
        rds.save()
        cols = []
        for c in data["columns"]:
            col = RawDataSetColumn.import_data(rds, c)
            cols.append(col.sort_order)
        for col in rds.rawdatasetcolumn_set.all():
            if col.sort_order not in cols:
                col.delete()
        return rds
    def __getstate__(self):
        return {
            "label": self.url,
            "columns": [ c.__getstate__() for c in self.rawdatasetcolumn_set.all() ],
        }
    def col_array_dict(self):
        arr = []
        d = {}
        for col in self.rawdatasetcolumn_set.all():
            arr.append(col)
            d[col.url] = col
        return (arr, d)
    def json(self):
        result = []
        for rec in self.rawdatarecord_set.all():
            result.append(rec.json())
        return result
    def csv_header(self):
        first_col = True
        out = ""
        for col in self.rawdatasetcolumn_set.all():
            if not first_col:
                out += ","
            out += col.csv()
            first_col = False
        out += "\n"
        return out
    def csv(self, writer):
        writer.write(self.csv_header())
        for rec in self.rawdatarecord_set.all():
            writer.write(rec.csv)
    class Meta: 
        unique_together = ('widget', 'url') 

class RawDataSetColumn(models.Model):
    rds = models.ForeignKey(RawDataSet)
    sort_order = models.IntegerField()
    heading = models.CharField(max_length=128)
    url = models.SlugField()
    description = models.TextField(null=True, blank=True)
    def csv(self):
        out = self.heading.replace('"', '""')
        if '"' in out or ',' in out:
            return '"%s"' % out
        else:
            return out
    def __unicode__(self):
        return "Column: %s" % self.heading
    def export(self):
        return {
            "sort_order": self.sort_order,
            "heading": self.heading,
            "description": self.description
        }
    def __getstate__(self):
        data = { "heading": self.heading }
        if self.description:
            data["description"] = self.description
        return data
    @classmethod
    def import_data(cls, rds, data):
        try:
            col = RawDataSetColumn.objects.get(rds=rds, sort_order=data["sort_order"])
        except RawDataSetColumn.DoesNotExist:
            col = RawDataSetColumn(rds=rds, sort_order=data["sort_order"])
        col.heading = data["heading"]
        col.description = data["description"]
        col.save()
        return col
    class Meta:
        unique_together = ("rds", "sort_order")
        ordering = ("rds", "sort_order")

