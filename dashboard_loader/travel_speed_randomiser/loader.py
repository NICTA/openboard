import datetime
import decimal
import random
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code

# Refresh every 10 minutes
refresh_rate = 60 * 10

def update_data(loader, verbosity=0):
    messages = []
    tz = pytz.timezone(settings.TIME_ZONE)
    now = datetime.datetime.now(tz)
    if now.hour in range(1, 14):
        set_statistic_data("road_speeds", "syd", "rt", "am_pm", "am")
        target = 39
    else:
        set_statistic_data("road_speeds", "syd", "rt", "am_pm", "pm")
        target = 42
    set_statistic_data("road_speeds", "syd", "rt", "target", target)
    speed_stat = get_statistic("road_speeds", "syd", "rt", "average_speed")
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
    set_statistic_data("road_speeds", "syd", "rt", "average_speed", new_speed, trend=trend, traffic_light_code=tlc)
    return messages
