import datetime
import httplib
import zipfile
import tempfile
import csv
import base64
import gc

from django import db
from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, call_in_transaction

from transport_static_loader.models import Agency, Calendar, CalendarDate, Route, Stop, Trip, StopTime

# refresh every 24 hours
refresh_rate = 60 * 60 * 24

def update_data(loader, verbosity=0):
    messages = []
    messages.extend(update_static_data(verbosity))
    return messages

def authentication_string():
    unencoded = "%s:%s" % (settings.TDX_USERNAME, settings.TDX_PASSWORD)
    encoded = base64.b64encode(unencoded)
    return "Basic %s" % encoded

def update_static_data(verbosity=0):
    messages = []
    http = httplib.HTTPSConnection("tdx.transportnsw.info")
    http.request("GET", 
            "https://tdx.transportnsw.info/download/files/full_greater_sydney_gtfs_static.zip",
            headers={"Authorization": authentication_string()}
    )
    tmp_zip = tempfile.TemporaryFile()
    resp = http.getresponse()
    while True:
        chunk = resp.read(8192)
        if chunk:
            tmp_zip.write(chunk)
        else:
            break
    tmp_zip.write(resp.read())
    gtfs_zip = zipfile.ZipFile(tmp_zip, "r")
    if verbosity > 5:
        print "Zip file downloaded"
    try:
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("agency.txt"), Agency, verbosity))
        if verbosity >= 5:
            print "Agencies loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("calendar.txt"), Calendar, verbosity))
        if verbosity >= 5:
            print "Calendars loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("calendar_dates.txt"), CalendarDate, verbosity))
        if verbosity >= 5:
            print "Calendar Dates loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("routes.txt"), Route, verbosity))
        if verbosity >= 5:
            print "Routes loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("stops.txt"), Stop, verbosity))
        if verbosity >= 5:
            print "Stops loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("trips.txt"), Trip, verbosity, batch_size=1000))
        if verbosity >= 5:
            print "Trips loaded"
        db.reset_queries()
        messages.extend(load_static_data(gtfs_zip.open("stop_times.txt"), StopTime, verbosity, batch_size=5000))
        if verbosity >= 5:
            print "Stop Times loaded"
    except LoaderException, e:
        messages.append(unicode(e))
    http.close()
    tmp_zip.close()
    if verbosity >= 1:
        messages.append("Static data updated")
    return messages

def load_static_data(csv_file, model, verbosity=0, batch_size=1):
    messages = []
    reader = csv.reader(csv_file)
    header_skipped = False
    batch = []
    saves = 0
    batch_creates = 0
    skipped = 0
    rows_read = 0
    for row in reader:
        if not header_skipped:
            header_skipped=True
            continue
        m = model.load_csv_row(row)
        if m.is_dirty:
            if batch_size == 1:
                m.save()
                saves += 1
            else:
                if m.id:
                    m.save()
                    saves += 1
                else:
                    batch.append(m)
                    if len(batch) >= batch_size:
                        model.objects.bulk_create(batch)
                        batch_creates += 1
                        batch = []
                        db.reset_queries()
        else:
            skipped += 1
        rows_read += 1
        if rows_read % 400000 == 0:
            db.reset_queries()
        if batch_size > 1 and rows_read % 10000 == 0 and verbosity >= 5:
            print "Processed %d rows:" % rows_read,
            if batch_size == 1:
                print "%d objects skipped, %d objects saved" % (skipped, saves)
            else:
                print "%d objects skipped, %d objects updated, %d batch creates (%d queued)" % (
                                        skipped,
                                        saves,
                                        batch_creates,
                                        len(batch))
    if batch:
        model.objects.bulk_create(batch)
        db.reset_queries()
        batch_creates += 1
    if verbosity >= 3:
        if batch_size == 1:
            messages.append("%s load complete: %d objects skipped, %d objects saved" % (model.__name__, skipped, saves))
        else:
            messages.append("%s load complete: %d objects skipped, %d objects updated, %d batch creates" % (
                                    model.__name__, 
                                    skipped,
                                    saves,
                                    batch_creates))
    if verbosity >= 5:
        if batch_size == 1:
            print "%s load complete: %d objects skipped, %d objects saved" % (model.__name__, skipped, saves)
        else:
            print "%s load complete: %d objects skipped, %d objects updated, %d batch creates" % (
                                    model.__name__, 
                                    skipped,
                                    saves,
                                    batch_creates)
    return messages

