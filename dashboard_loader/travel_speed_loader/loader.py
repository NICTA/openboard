import datetime
import decimal
import random
import pytz
import httplib
import json

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code
from travel_speed_loader.models import Road, RoadSection

# Refresh every 2 minutes
refresh_rate = 60 * 2

def get_livetrafficdata(http, filename, label, messages, verbosity=0):
    http.request("GET", "http://livetraffic.rta.nsw.gov.au/traffic/travel_time/%s" % filename)
    resp = http.getresponse()
    return json.load(resp)["features"]

def load_speeds(features, name, am, target, stats, messages, verbosity=0):
    try:
        road = Road.objects.get(name=name)
    except Road.DoesNotExist:
        if verbosity > 0:
            messages.append("Road %s not defined" % name)
        return
    road_dist = 0
    road_travel_time = 0
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
        if (fid[0] in road.am_direction and am) or (fid[0] in road.pm_direction and not am):
            stats["total_travel_time"]  += travel_time
            stats["total_distance"]  += distance
            road_dist += distance
            road_travel_time += travel_time
    speed_stat = get_statistic("road_speeds", "syd", "rt", name)
    speed = float(road_distance) / (float(road_travel_time) / 60.0)
    if speed < target:
        tlc = get_traffic_light_code(speed_stat, "poor")
    else:
        tlc = get_traffic_light_code(speed_stat, "good")
    if verbosity >=2:
        messages.append("Saving road speed for %s" % name)
    set_statistic_data("road_speeds", "syd", "rt", name, speed, traffic_light_code=tlc)
        

def update_data(loader, verbosity=0):
    messages = []
    tz = pytz.timezone(settings.TIME_ZONE)
    now = datetime.datetime.now(tz)
    if now.hour in range(1, 14):
        am = True
        set_statistic_data("road_speeds", "syd", "rt", "am_pm", "am")
        target = 39
    else:
        am = False
        set_statistic_data("road_speeds", "syd", "rt", "am_pm", "pm")
        target = 37
    set_statistic_data("road_speeds", "syd", "rt", "target", target)
    http = httplib.HTTPConnection("livetraffic.rta.nsw.gov.au")
    m1_features = get_livetrafficdata(http, "f3.json", "M1", messages, verbosity)
    m2_features = get_livetrafficdata(http, "m2.json", "M2", messages, verbosity)
    m4_features = get_livetrafficdata(http, "m4.json", "M4", messages, verbosity)
    m7_features = get_livetrafficdata(http, "m7.json", "M7", messages, verbosity)
    http.close()
    total_stats = {
        'total_travel_time': 0,
        'total_distance': 0
    }
    load_speeds(m1_features, "M1", am, target,total_stats, messages, verbosity)
    load_speeds(m2_features, "M2", am, target,total_stats, messages, verbosity)
    load_speeds(m4_features, "M4", am, target,total_stats, messages, verbosity)
    load_speeds(m7_features, "M7", am, target,total_stats, messages, verbosity)
    speed_stat = get_statistic("road_speeds", "syd", "rt", "average_speed")
    last_speed = speed_stat.get_data().intval
    new_speed = float(total_stats["total_travel_time"])/(float(total_stats["total_distance"])/60.0)
    if abs(last_speed - new_speed) < 0.1:
        trend = 0
    elif last_speed > new_speed:
        trend = -1
    else:
        trend = 1
    if new_speed < target:
        tlc = get_traffic_light_code(speed_stat, "poor")
    else:
        tlc = get_traffic_light_code(speed_stat, "good")
    if verbosity > 2:
        messages.append("Writing new road_speed: %f"  % new_speed)
    set_statistic_data("road_speeds", "syd", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages

