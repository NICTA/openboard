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

import datetime
import decimal
import random
import pytz
import httplib
import json

from django.conf import settings

from dashboard_loader.loader_utils import *

# Refresh every 5 minute
refresh_rate = 60 * 5

# Read json file from livetraffic website and parse as json
def get_livehazarddata(http, filename, messages, verbosity=0):
    http.request("GET", "http://livetraffic.rta.nsw.gov.au/traffic/hazards/%s" % filename)
    resp = http.getresponse()
    text = resp.read()
    # Standard JSON should be UTF-8, but ISO-8859-1 characters have been observed.
    utf = unicode(text, 'iso-8859-1')
    return json.loads(utf)["features"]

# Constants for handling traffic light coding
BAD = 0
POOR = 1
GOOD = 2
severity_tlc = [ "bad", "poor", "good" ]

# Function called when the loader is run.
def update_data(loader, verbosity=0):
    messages = []
    now = datetime.datetime.now(tz)
    http = httplib.HTTPConnection("livetraffic.rta.nsw.gov.au")
    # Load all hazard types.
    hazards = get_livehazarddata(http, "alpine-open.json", messages, verbosity)
    hazards.extend(get_livehazarddata(http, "fire-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "flood-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "incident-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "majorevent-open.json", messages, verbosity))
    hazards.extend(get_livehazarddata(http, "roadwork-open.json", messages, verbosity))
    incidents = { "count": 0, "severity_tlc": GOOD }
    majors = []
    for hazard in hazards:
        if hazard["properties"].get("start"):
            if epoch_convert(hazard["properties"]["start"], tz) > now:
                # Hazard Not started yet
                continue
        if hazard["properties"].get("end"):
            if epoch_convert(hazard["properties"]["end"], tz) < now:
                # Hazard Finished
                continue
        if hazard["properties"]["isMajor"]:
            majors.append(hazard["properties"]["headline"])
        for road in hazard["properties"]["roads"]:
            region = road["region"]
            incidents["count"] += 1
            # severity_tlc is the tlc code of the most severe incident seen so far.
            if hazard["properties"]["impactingNetwork"] and hazard["properties"]["isMajor"]:
                # "Major" incident that is "impacting network" = BAD (red)
                if incidents["severity_tlc"] > BAD:
                    incidents["severity_tlc"] = BAD
            elif hazard["properties"]["impactingNetwork"] or hazard["properties"]["isMajor"]:
                # "Major" incident that isn't "impacting network" 
                # (or non-major incident that is impacting network) = POOR (amber)
                if incidents["severity_tlc"] > POOR:
                    incidents["severity_tlc"] = POOR
    call_in_transaction(load_incidents, incidents, majors, now)
    http.close()
    if verbosity > 0:
        messages.append("Data loaded")
    return messages

# Load data into widgets (called inside database transaction from update_data
def load_incidents(incidents, majors, now):
    set_statistic_data("traffic_incidents", "nsw", "rt", "incidents", incidents["count"],
                            traffic_light_code=severity_tlc[incidents["severity_tlc"]])
    set_highlight = False
    then = now - datetime.timedelta(seconds=10)
    clear_statistic_list("traffic_incidents", "nsw", "rt", "highlight")
    clear_statistic_list("traffic_incidents", "nsw", "rt", "major_incidents")
    sort_order = 10
    if len(majors) == 0:
        add_statistic_list_item("traffic_incidents", "nsw", "rt", "highlight", "No current major incidents", sort_order)
        add_statistic_list_item("traffic_incidents", "nsw", "rt", "major_incidents", "No current major incidents", sort_order)
    for major in majors:
        add_statistic_list_item("traffic_incidents", "nsw", "rt", "highlight", major, sort_order)
        add_statistic_list_item("traffic_incidents", "nsw", "rt", "major_incidents", major, sort_order)
        if sort_order >= 100:
            break
        sort_order += 10

# Convert ms since epoch to datetime.
def epoch_convert(ms, tz):
    s = ms / 1000.0
    return datetime.datetime.fromtimestamp(s, tz)


