import datetime
import decimal
import random
import pytz
import httplib
import json

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code
from travel_speed_loader.models import Road, RoadSection

# Refresh every 10 minutes
refresh_rate = 60 * 10

def get_livetrafficdata(http, filename, label, messages, verbosity=0):
    http.request("GET", "http://livetraffic.rta.nsw.gov.au/traffic/travel_time/%s" % filename)
    resp = http.getresponse()
    if verbosity >= 3:
        messages.append("%s returned %d" % (label, resp.status))
    return json.load(resp)["features"]

def check_features(features, roadname, messages, verbosity=0):
    try:
        road = Road.objects.get(name=roadname)
    except Road.DoesNotExist:
        road = Road(name=roadname)
        road.am_direction = features[0]["id"][0]
        if road.am_direction == 'N':
            road.pm_direction = 'S'
        elif road.am_direction == 'S':
            road.pm_direction = 'N'
        elif road.am_direction == 'W':
            road.pm_direction = 'E'
        else:
            road.pm_direction = 'W'
        road.save()
    for f in features:
        fid = f["id"]
        try:
            section = RoadSection.objects.get(road=road,label=fid)
        except RoadSection.DoesNotExist:
            section = RoadSection(road=road,label=fid)
        section.route_direction = fid[0]
        if f["properties"].get("direction"):
            section.direction=f["properties"]["direction"]
        else:
            section.direction=section.route_direction
        section.origin=f["properties"]["fromDisplayName"]
        section.destination=f["properties"]["toDisplayName"]
        # HACK DATA FIX!!!!
        if roadname == "M2" and fid == "ETOTAL":
            if section.origin != "M7":
                section.origin = "M7"
            else:
                messages.append("HACK DATA FIX no longer required")
        section.save()

def load_speeds(features, name, am, target, stats, messages, verbosity=0):
    try:
        road = Road.objects.get(name=name)
    except Road.DoesNotExist:
        if verbosity > 0:
            messages.append("Road %s not defined" % name)
        return
    for f in features:
        fid = f["id"]
        if fid[1:] != "TOTAL":
            continue
        try:
            section = RoadSection.objects.get(road=road, label=fid)
        except RoadSection.DoesNotExist:
            if verbosity > 0:
                messages.append("Road section %s(%s) not defined" % (fid,name))
            return
        distance = section.length
        travel_time = f["properties"]["travelTimeMinutes"]
        stats["total_travel_time"]  += travel_time
        stats["total_distance"]  += distance
        if (fid[0] == road.am_direction and am) or (fid[0] == road.pm_direction and not am):
            speed_stat = get_statistic("road_speeds", "rt", name)
            speed = float(distance) / (float(travel_time) / 60.0)
            if speed < target:
                tlc = get_traffic_light_code(speed_stat, "bad")
            elif speed < target * 1.15:
                tlc = get_traffic_light_code(speed_stat, "poor")
            else:
                tlc = get_traffic_light_code(speed_stat, "good")
            set_statistic_data("road_speeds", "rt", name, speed, traffic_light_code=tlc)

def update_data(loader, verbosity=0):
    messages = []
    tz = pytz.timezone(settings.TIME_ZONE)
    now = datetime.datetime.now(tz)
    if now.hour in range(1, 14):
        am = True
        set_statistic_data("road_speeds", "rt", "am_pm", "am")
        target = 39
    else:
        am = False
        set_statistic_data("road_speeds", "rt", "am_pm", "pm")
        target = 42
    set_statistic_data("road_speeds", "rt", "target", target)
    http = httplib.HTTPConnection("livetraffic.rta.nsw.gov.au")
    m1_features = get_livetrafficdata(http, "f3.json", "M1", messages, verbosity)
    m2_features = get_livetrafficdata(http, "m2.json", "M2", messages, verbosity)
    m4_features = get_livetrafficdata(http, "m4.json", "M4", messages, verbosity)
    m7_features = get_livetrafficdata(http, "m7.json", "M7", messages, verbosity)
    check_features(m1_features, "M1", messages, verbosity)
    check_features(m2_features, "M2", messages, verbosity)
    check_features(m4_features, "M4", messages, verbosity)
    check_features(m7_features, "M7", messages, verbosity)
    total_stats = {
        'total_travel_time': 0,
        'total_distance': 0
    }
    load_speeds(m1_features, "M1", am, target,total_stats, messages, verbosity)
    load_speeds(m2_features, "M2", am, target,total_stats, messages, verbosity)
    load_speeds(m4_features, "M4", am, target,total_stats, messages, verbosity)
    load_speeds(m7_features, "M7", am, target,total_stats, messages, verbosity)
    speed_stat = get_statistic("road_speeds", "rt", "average_speed")
    last_speed = speed_stat.get_data().intval
    new_speed = float(total_stats["total_travel_time"])/(float(total_stats["total_distance"])/60.0)
    if abs(last_speed - new_speed) < 0.1:
        trend = 0
    elif last_speed > new_speed:
        trend = -1
    else:
        trend = 1
    if new_speed < target:
        tlc = get_traffic_light_code(speed_stat, "bad")
    elif new_speed < target * 1.15:
        tlc = get_traffic_light_code(speed_stat, "poor")
    else:
        tlc = get_traffic_light_code(speed_stat, "good")
    set_statistic_data("road_speeds", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages


def randomiser_stub():
    message = []
    target=42
    speed_stat = get_statistic("road_speeds", "rt", "average_speed")
    last_speed = speed_stat.get_data().intval
    new_speed = int(round(random.gauss(45, 3)))
    if last_speed > new_speed:
        trend = -1
    elif last_speed < new_speed:
        trend = 1
    else:
        trend = 0
    if new_speed < target:
        tlc = get_traffic_light_code(speed_stat, "bad")
    elif new_speed < target * 1.15:
        tlc = get_traffic_light_code(speed_stat, "poor")
    else:
        tlc = get_traffic_light_code(speed_stat, "good")
    set_statistic_data("road_speeds", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages
