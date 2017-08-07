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

from widget_def.models.widget_definition import WidgetDefinition
from widget_def.parametisation import parametise_label, resolve_pval
from widget_def.view_tools import csv_escape
from widget_def.model_json_tools import *


class RawDataSet(models.Model, WidgetDefJsonMixin):
    """
    Defines a "raw data set" for a widget.

    A raw data set can be thought of as a CSV file*. It is not stored as such, but that's how it is 
    usually delivered (although json is supported as well).

    * or a family of CSV files if the widget is parametised.
    """
    export_def = {
        "widget": JSON_INHERITED("raw_datasets"),
        "url": JSON_ATTR(),
        "filename": JSON_ATTR(),
        "columns": JSON_RECURSEDOWN("RawDataSetColumn", "columns", "rds", "url", app="widget_def")
    }
    export_lookup = { "widget": "widget", "url": "url" }
    api_state_def = {
        "label": JSON_ATTR(attribute="url"),
        "name": JSON_ATTR(attribute="name", parametise=True),
        "columns": JSON_RECURSEDOWN("RawDataSetColumn", "columns", "rds", "url", app="widget_def")
    }
    widget = models.ForeignKey(WidgetDefinition, related_name="raw_datasets", help_text="The Widget this dataset belongs to")
    url = models.SlugField(verbose_name="label", help_text="A short symbolic label for the raw dataset, as used in the API")
    name = models.CharField(max_length=128, help_text="A longer more descriptive name for the raw dataset. May be parametised.")
    filename = models.CharField(max_length=128, help_text="The filename for the generated csv file. (Should end in '.csv').")
    def __unicode__(self):
        return "%s.%s (%s)" % (self.widget.family.url, self.url, self.filename)
    def col_array_dict(self):
        """
        Return a tuple consisting of:

        1) An array of :model:`RawDataSetColumn` objects.
        2) A dictionary of :model:`RawDataSetColumn` objects, keyed by their label (url).
        """
        arr = []
        d = {}
        for col in self.columns.all():
            arr.append(col)
            d[col.url] = col
        return (arr, d)
    def json(self, pval=None, view=None):
        """Return a json-serialisable dump of this dataset."""
        result = []
        pval = resolve_pval(self.widget.parametisation, view=view, pval=pval)
        if pval:
            for rec in self.rawdatarecord_set.all(param_value=pval):
                yield rec.json()
        else:
            for rec in self.rawdatarecord_set.all():
                yield rec.json()
    def csv_header(self, view=None):
        """Return a CSV header row for the dataset."""
        first_col = True
        out = ""
        for col in self.columns.all():
            if not first_col:
                out += ","
            out += col.csv(view)
            first_col = False
        out += "\n"
        return out
    def csv(self, writer, view=None):
        """Write out a CSV for the dataset to the provided writer (e.g. an HttpResponse object)"""
        pval = resolve_pval(self.widget.parametisation, view=view)
        writer.write(self.csv_header(view))
        if pval:
            for rec in self.rawdatarecord_set.filter(param_value=pval):
                writer.write(rec.csv)
        else:
            for rec in self.rawdatarecord_set.all():
                writer.write(rec.csv)
    class Meta: 
        unique_together = [ ('widget', 'url') ,
                            ('widget', 'name') ,
        ]
        ordering = ('widget', 'url')

class RawDataSetColumn(models.Model, WidgetDefJsonMixin):
    """A column in a :model:`widget_def.RawDataSet`"""
    export_def = {
        "rds": JSON_INHERITED("columns"),
        "sort_order": JSON_IMPLIED(),
        "heading": JSON_ATTR(),
        "description": JSON_ATTR(),
        "url": JSON_ATTR()
    }
    export_lookup = { "rds": "rds", "url": "url" }
    api_state_def = {
        "heading": JSON_ATTR(parametise=True),
        "description": JSON_ATTR(parametise=True, decider="description")
    }
    rds = models.ForeignKey(RawDataSet, related_name="columns", help_text="The raw dataset")
    sort_order = models.IntegerField(help_text="Determines the column order within a raw dataset")
    heading = models.CharField(max_length=128, help_text="The column heading, as used in a csv file")
    url = models.SlugField(help_text="A short symbolic name for the column, used by default in a json file")
    description = models.TextField(null=True, blank=True, help_text="A detailed description of the column")
    def widget(self):
        return self.rds.widget
    def csv(self, view=None):
        """Return a CSV escaped heading for this column"""
        return csv_escape(parametise_label(self.rds.widget, view, self.heading))
    def __unicode__(self):
        return "Column: %s" % self.heading
    class Meta:
        unique_together = ("rds", "sort_order")
        ordering = ("rds", "sort_order")

