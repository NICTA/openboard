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

from widget_def.models import RawDataSet
from widget_data.models import RawDataRecord, RawData

from interface import LoaderException

def get_rawdataset(widget_url, actual_location_url, actual_frequency_url, rds_url):
    """Get a RawDataSet object by urls."""
    try:
        return RawDataSet.objects.get(widget__family__url=widget_url,
                                widget__actual_location__url=actual_location_url,
                                widget__actual_frequency__url=actual_frequency_url,
                                url=rds_url)
    except RawDataSet.DoesNotExist:
        raise LoaderException("Raw Dataset %s of widget %s(%s,%s) does not exist" % (rds_url, widget_url, actual_location_url, actual_frequency_url))

def clear_rawdataset(rds):
    """Clear all data for a RawDataSet object"""
    rds.rawdatarecord_set.all().delete()

def add_rawdatarecord(rds, sort_order, *args, **kwargs):
    """Add a record to a RawDataSet.

rds: The Raw Data Set object.
sort_order: The order of the new record in the data set.

The data may be supplied as either positional arguments (column
order from left to right) or keyword arguments (keys are the defined
column urls).
"""
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

