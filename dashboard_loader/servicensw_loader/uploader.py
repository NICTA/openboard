import csv
import decimal
from dashboard_loader.loader_utils import LoaderException, get_statistic, set_statistic_data, set_actual_frequency_display_text

groups = [ "upload_all", "upload_servicensw" ]

file_format = {
    "format": "csv",
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
# ('Service Centre', 'Data for service centre counters'), 
#                    ('Contact Centre', 'Data for call centres'), 
#                    ('Digital', 'Data for web site'), 
            ],
        }
    ],
}

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        reader = csv.reader(fh)
        heading_read = False
        for row in reader:
            if not heading_read:
                heading_read = True
                continue
            if len(row) != 4:
                raise LoaderException("Row in Service NSW upload file does not have 4 columns")
            sdc = row[0]
            visits = int(row[1])
            if row[2]:
                csat = decimal.Decimal(row[2])
            else:
                csat = None
            visit_time = row[3]
            if "Centre" in sdc:
                visit_stat = get_statistic("service_nsw_svc_counters", "syd", "day", "visits") 
                other_stat = get_statistic("service_nsw_svc_counters", "syd", "day", "satisfaction") 
                other_val = csat
            elif "Phone" in sdc or "Contact" in sdc:
                visit_stat = get_statistic("service_nsw_svc_calls", "syd", "day", "callers") 
                other_stat = get_statistic("service_nsw_svc_calls", "syd", "day", "satisfaction")
                other_val = csat
            elif "Digital" in sdc:
                visit_stat = get_statistic("service_nsw_svc_www", "syd", "day", "visits") 
                other_stat = get_statistic("service_nsw_svc_www", "syd", "day", "duration") 
                other_val = normalise_time(visit_time)
            else:
                raise LoaderException("Unrecognised Service Delivery Channel in Service NSW upload: %s" % sdc)
            update_stats(visit_stat, visits, other_stat, other_val, actual_freq_display)
            if verbosity > 1:
                messages.append("Updated stats for %s" % sdc)
        return messages
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))

def update_stats(visit_stat, visits, other_stat, other_val, actual_freq_display):
    old_visits = visit_stat.get_data()
    if old_visits:
        old_visits = old_visits.value()
# if old_visits < visits:
#        trend = 1
#    elif old_visits == visits:
#        trend = 0
#    else:
#        trend = -1
    set_statistic_data(visit_stat.tile.widget.family.url, visit_stat.tile.widget.actual_location.url,
                    visit_stat.tile.widget.actual_frequency.url, visit_stat.url,
                    visits) #, trend=trend)
#    if old_wait < new_wait:
#        trend = 1
#    elif old_wait == new_wait:
#        trend = 0
#    else:
#        trend = -1
    set_statistic_data(other_stat.tile.widget.family.url, other_stat.tile.widget.actual_location.url,
                    other_stat.tile.widget.actual_frequency.url, other_stat.url,
                    other_val) # , trend=trend)
    if actual_freq_display:
        set_actual_frequency_display_text(visit_stat.tile.widget.family.url, 
                    visit_stat.tile.widget.actual_location.url, visit_stat.tile.widget.actual_frequency.url, 
                    actual_freq_display)

def normalise_time(t):
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
        raise LoaderException("Invalid wait time string in Service NSW upload: %s" % t)
    if mins >= 60 or secs >= 60:
        raise LoaderException("Invalid wait time string in Service NSW upload: %s" % t)
    mins = 60 * hours + mins
    return "%02d:%02d" % (mins, secs)

