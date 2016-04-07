#   Copyright 2015,2016 NICTA
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

import csv
import decimal
from dashboard_loader.loader_utils import *

# These are the names of the groups that have permission to upload data for this uploader.
# If the groups do not exist they are created on registration.
groups = [ "upload_all", "upload_frontlineservice" ]

# This describes the file format.  It is used to describe the format by both
# "python manage.py upload_data frontlineservice_uploader" and by the uploader 
# page in the data admin GUI.
file_format = {
    # format:  Either "csv", "xls", or "zip"
    "format": "csv",
    # sheets: csv formats should only have one sheet.  For "zip", sheets are 
    #         csv files within the zip file
    "sheets": [
        {
            "name": "CSV Sheet",
            "cols": [
                    ('A', 'Service Delivery Channel (identifies row)'),
                    ('B', 'Number of visits'),
                    ('C', 'CSAT (Customer satisfaction %) - Service centres and phone service only'),
                    ('D', 'Average visit time (hh:mm:ss) - Digital service only'),
            ],
            "rows": [
                    ('1', 'Column headers'),
                    ('Service Centres', 'Data for service centre counters'), 
                    ('Phone Service', 'Data for call centres'), 
                    ('Digital Service', 'Data for web site'), 
            ],
        }
    ],
}

# The function called when uploading a file.
def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        # Read the fh file handle as a CSV file.
        reader = csv.reader(fh)
        heading_read = False
        for row in reader:
            # Skip the first row (the heading row)
            if not heading_read:
                heading_read = True
                continue
            if len(row) != 4:
                raise LoaderException("Row in Frontline Service upload file does not have 4 columns")
            sdc = row[0]
            visits = int(row[1])
            if row[2]:
                csat = int(row[2])
            else:
                csat = None
            visit_time = row[3]
            # Determine the stats to write to for this row.
            if "Centre" in sdc:
                visit_stat = get_statistic("svc_counters", "syd:day", "visits") 
                other_stat = get_statistic("svc_counters", "syd:day", "satisfaction") 
                other_val = csat
            elif "Phone" in sdc or "Contact" in sdc:
                visit_stat = get_statistic("svc_calls", "syd:day", "callers") 
                other_stat = get_statistic("svc_calls", "syd:day", "satisfaction")
                other_val = csat
            elif "Digital" in sdc:
                visit_stat = get_statistic("svc_www", "syd:day", "visits") 
                other_stat = get_statistic("svc_www", "syd:day", "duration") 
                other_val = normalise_time(visit_time)
            else:
                raise LoaderException("Unrecognised Service Delivery Channel in Frontline Service upload: %s" % sdc)
            update_stats(visit_stat, visits, other_stat, other_val, actual_freq_display)
            if verbosity > 1:
                messages.append("Updated stats for %s" % sdc)
        return messages
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))

def update_stats(visit_stat, visits, other_stat, other_val, actual_freq_display):
    # Set statistic data
    set_stat_data(visit_stat, visits)
    set_stat_data(other_stat, other_val)
    # Set actual frequency display text
    if actual_freq_display:
        set_widget_actual_frequency_display_text(visit_stat.tile.widget, actual_freq_display)

def normalise_time(t):
    # Convert hh:mm:ss to mm:ss (e.g. "01:10:10"  ->  "70:10")
    if t is None:
        return "00:00"
    bits = t.split(":")
    if len(bits) == 3:
        hours = int(bits[0])
        mins = int(bits[1])
        secs = int(bits[2])
    elif len(bits) == 2:
        secs = int(bits[1])
        mins = int(bits[0])
        hours = mins / 60
        mins = mins % 60 
    elif len(bits) == 1:
        secs = int(bits[0])
        mins = secs / 60
        secs = secs % 60
        hours = mins / 60
        mins = mins % 60 
    else:
        raise LoaderException("Invalid wait time string in Frontline Service upload: %s" % t)
    if mins >= 60 or secs >= 60:
        raise LoaderException("Invalid wait time string in Frontline Service upload: %s" % t)
    mins = 60 * hours + mins
    return "%02d:%02d" % (mins, secs)

