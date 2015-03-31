import datetime
import decimal
import random
import pytz
import httplib
import json

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code, call_in_transaction, clear_statistic_list, add_statistic_list_item
from traffic_incident_loader.models import MajorIncident

# Refresh every 5 minute
refresh_rate = 9
api_refresh_rate = 60 * 5

def epoch_convert(ms, tz):
    s = ms / 1000.0
    return datetime.datetime.fromtimestamp(s, tz)

def get_livehazarddata(http, filename, messages, verbosity=0):
    http.request("GET", "http://livetraffic.rta.nsw.gov.au/traffic/hazards/%s" % filename)
    resp = http.getresponse()
    return json.load(resp)["features"]

severity_tlc = [ "bad", "poor", "good" ]

def update_data(loader, verbosity=0):
    tz = pytz.timezone(settings.TIME_ZONE)
    if loader.last_api_access and datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)) - loader.last_api_access < datetime.timedelta(seconds=api_refresh_rate):
        messages = rotate_data(tz, verbosity)
    else:
        messages = reload_data(loader, tz, verbosity)
    return messages

def rotate_data(tz, verbosity=0):
    messages = []
    mi = MajorIncident.objects.all().order_by("last_featured")[0]
    set_statistic_data("traffic_incidents", "nsw", "rt", "highlight", mi.text)
    mi.last_featured = datetime.datetime.now(tz)
    mi.save()
    messages.append("Highlight rotated")
    return messages

def reload_data(loader, tz, verbosity=0):
    messages = []
    now = datetime.datetime.now(tz)
    http = httplib.HTTPConnection("livetraffic.rta.nsw.gov.au")
    hazards = get_livehazarddata(http, "alpine-open.json", messages, verbosity)
    hazards.extend(get_livehazarddata(http, "fire-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "flood-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "incident-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "majorevent-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "roadwork-open.json", messages, verbosity))
    incidents = { "count": 0, "severity_tlc": 2 }
    majors = []
    for hazard in hazards:
        if hazard["properties"].get("start"):
            if epoch_convert(hazard["properties"]["start"], tz) > now:
                # Not started yet
                if verbosity >= 5:
                    print "Skipping: not started yet"
                continue
        if hazard["properties"].get("end"):
            if epoch_convert(hazard["properties"]["end"], tz) < now:
                # Finished
                if verbosity >= 5:
                    print "Skipping: finished"
                continue
        if verbosity >= 5:
            print hazard["properties"]["headline"]
        if hazard["properties"]["isMajor"]:
            majors.append(hazard["properties"]["headline"])
        for road in hazard["properties"]["roads"]:
            region = road["region"]
            incidents["count"] += 1
            if hazard["properties"]["impactingNetwork"] and hazard["properties"]["isMajor"]:
                if incidents["severity_tlc"] > 0:
                    incidents["severity_tlc"] = 0
            elif hazard["properties"]["impactingNetwork"] or hazard["properties"]["isMajor"]:
                if incidents["severity_tlc"] > 1:
                    incidents["severity_tlc"] = 1
    call_in_transaction(load_incidents, incidents, majors, now)
    http.close()
    loader.last_api_access = now
    loader.save()
    messages.append("Data reloaded")
    # set_statistic_data("road_speeds", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages

def load_incidents(incidents, majors, now):
    MajorIncident.objects.all().delete()
    set_statistic_data("traffic_incidents", "nsw", "rt", "incidents", incidents["count"],
                            traffic_light_code=severity_tlc[incidents["severity_tlc"]])
    set_highlight = False
    then = now - datetime.timedelta(seconds=10)
    for major in majors:
        m = MajorIncident(text=major)
        if not set_highlight:
            set_statistic_data("traffic_incidents", "nsw", "rt", "highlight", major)
            set_highlight = True
            m.last_featured = now
        else:
            m.last_featured = then
        m.save()

