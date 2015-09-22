from widget_def.models import RawDataSet
from widget_data.models import RawDataRecord, RawData

from interface import LoaderException

def get_rawdataset(widget_url, actual_location_url, actual_frequency_url, rds_url):
    try:
        return RawDataSet.objects.get(widget__family__url=widget_url,
                                widget__actual_location__url=actual_location_url,
                                widget__actual_frequency__url=actual_frequency_url,
                                url=rds_url)
    except RawDataSet.DoesNotExist:
        raise LoaderException("Raw Dataset %s of widget %s(%s,%s) does not exist" % (rds_url, widget_url, actual_location_url, actual_frequency_url))

def clear_rawdataset(rds):
    rds.rawdatarecord_set.all().delete()

def add_rawdatarecord(rds, sort_order, *args, **kwargs):
    record = RawDataRecord(rds=rds, sort_order=sort_order)
    record.save()
    (colarray, coldict ) = rds.col_array_dict()
    for i in range(len(args)):
        cell = RawData(record=record, column=colarray[i], value=unicode(args[i]))
        cell.save()
    for k,v in kwargs.items():
        cell = RawData(record=record, column=coldict[k], value=unicode(v))
        cell.save()
    record.update_csv()

