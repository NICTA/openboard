import datetime
import decimal
import random
import pytz
import httplib
import json

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code, call_in_transaction, clear_statistic_list, add_statistic_list_item
from travel_speed_loader.models import Road, RoadSection

# Refresh every 1 minute
refresh_rate = 60

def get_livehazarddata(http, filename, messages, verbosity=0):
    http.request("GET", "http://livetraffic.rta.nsw.gov.au/traffic/hazards/%s" % filename)
    resp = http.getresponse()
    return json.load(resp)["features"]

severity_tlc = [ "bad", "poor", "good" ]

def update_data(loader, verbosity=0):
    messages = []
    tz = pytz.timezone(settings.TIME_ZONE)
    http = httplib.HTTPConnection("livetraffic.rta.nsw.gov.au")
    hazards = get_livehazarddata(http, "alpine-open.json", messages, verbosity)
    hazards.extend(get_livehazarddata(http, "fire-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "flood-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "incident-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "majorevent-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "roadwork-open.json", messages, verbosity))
    incidents = {
        "syd": {},
        "nsw": {},
    }
    for hazard in hazards:
        for road in hazard["properties"]["roads"]:
            region = road["region"]
            if region.startswith("SYD_"):
                if not incidents["syd"].get(region):
                    incidents["syd"][region] = { "count": 0, "severity_tlc": 2 }
                incidents["syd"][region]["count"] += 1
                if hazard["properties"]["impactingNetwork"] and hazard["properties"]["isMajor"]:
                    if incidents["syd"][region]["severity_tlc"] > 0:
                        incidents["syd"][region]["severity_tlc"] = 0
                elif hazard["properties"]["impactingNetwork"] or hazard["properties"]["isMajor"]:
                    if incidents["syd"][region]["severity_tlc"] > 1:
                        incidents["syd"][region]["severity_tlc"] = 1
                region = u"SYDNEY"                
            if not incidents["nsw"].get(region):
                incidents["nsw"][region] = { "count": 0, "severity_tlc": 2 }
            incidents["nsw"][region]["count"] += 1
            if hazard["properties"]["impactingNetwork"] and hazard["properties"]["isMajor"]:
                if incidents["nsw"][region]["severity_tlc"] > 0:
                    incidents["nsw"][region]["severity_tlc"] = 0
            elif hazard["properties"]["impactingNetwork"] or hazard["properties"]["isMajor"]:
                if incidents["nsw"][region]["severity_tlc"] > 1:
                    incidents["nsw"][region]["severity_tlc"] = 1
    call_in_transaction(load_incidents, incidents)
    http.close()
    # set_statistic_data("road_speeds", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages

def load_incidents(incidents):
    clear_statistic_list("traffic_incidents_syd", "rt", "incidents")
    index = 0
    for (region, stats) in incidents["syd"].items():
        add_statistic_list_item("traffic_incidents_syd", "rt", "incidents",
                                stats["count"], (stats["severity_tlc"] * 100) + index,
                                label=region, traffic_light_code=severity_tlc[stats["severity_tlc"]])
        index += 1
    clear_statistic_list("traffic_incidents_nsw", "rt", "incidents")
    index = 0
    for (region, stats) in incidents["nsw"].items():
        add_statistic_list_item("traffic_incidents_nsw", "rt", "incidents",
                                stats["count"], (stats["severity_tlc"] * 100) + index,
                                label=region, traffic_light_code=severity_tlc[stats["severity_tlc"]])
        index += 1
    return None



