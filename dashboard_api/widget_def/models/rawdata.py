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
            raw = RawDataSet.objects.get(widget=widget, url=data["url"])
        except RawDataSet.DoesNotExist:
            raw = RawDataSet(widget=widget, url=data["url"])
        raw.filename = data["filename"]
        raw.save()
        cols = []
        for c in data["columns"]:
            col = RawDataSetColumn.import_data(raw, c)
            cols.append(col.sort_order)
        for col in self.rawdatasetcolumn_set.all():
            if col.sort_order not in cols:
                col.delete()
        return raw
    def __getstate__(self):
        return {
            "url": self.url,
        }
    def col_array_dict(self):
        arr = []
        d = {}
        for col in self.rawdatasetcolumn_set.all():
            arr.append(col)
            d[col.url] = col
        return (arr, d)
    def csv_header(self):
        first_col = True
        for col in rds.rawdatacolumn_set.all():
            if not first_col:
                out += ","
            out += col.csv()
            first_col = False
        out += "\n"
        return out
    def csv(self):
        out = self.csv_header()
        for rec in self.rawdatarecord_set.all():
            out += rec.csv()
        return out
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

