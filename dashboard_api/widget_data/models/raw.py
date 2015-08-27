from django.db import models

# Create your models here.

class RawDataRecord(models.Model):
    rds = models.ForeignKey("widget_def.RawDataSet")
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
        unique_together=("rds", "sort_order")
        ordering = ("rds", "sort_order")

class RawData(models.Model):
    record = models.ForeignKey(RawDataRecord)
    column = models.ForeignKey("widget_def.RawDataSetColumn")
    value = models.CharField(max_length=1024, blank=True)
    def csv(self):
        out = self.value.replace('"', '""')
        if '"' in out or ',' in out:
            return '"%s"' % out
        else:
            return out
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

