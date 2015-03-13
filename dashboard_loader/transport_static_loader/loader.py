import datetime
import httplib
import zipfile
import tempfile
import csv
import base64

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
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("trips.txt"), Trip, verbosity))
        if verbosity >= 5:
            print "Trips loaded"
        messages.extend(call_in_transaction(load_static_data,gtfs_zip.open("stop_times.txt"), StopTime, verbosity))
        if verbosity >= 5:
            print "Stop Times loaded"
    except LoaderException, e:
        messages.append(unicode(e))
    http.close()
    tmp_zip.close()
    if verbosity >= 1:
        messages.append("Static data updated")
    return messages

def load_static_data(csv_file, model, verbosity=0):
    messages = []
    reader = csv.reader(csv_file)
    header_skipped = False
    for row in reader:
        if not header_skipped:
            header_skipped=True
            continue
        m = model.load_csv_row(row)
        m.save()
    if verbosity > 3:
        messages.append("%s load complete" % model.__name__)
    return messages

