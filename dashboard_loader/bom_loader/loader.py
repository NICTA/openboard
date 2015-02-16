import time
import datetime
import decimal
from tempfile import TemporaryFile
from ftplib import FTP
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, update_loader, set_statistic_data, clear_statistic_data,get_icon, get_statistic

# Refresh data every 5 minutes
refresh_rate = 60*5
# refresh_rate = 1

# From  http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=36&p_display_type=dataFile&p_startYear=&p_c=&p_stn_num=066062
# Should be updated every now and then.
monthly_avg_temp = [
    25.9, 25.8, 24.8, 
    22.4, 19.5, 17.0, 
    16.3, 17.8, 20.0, 
    22.1, 23.6, 25.2,
]

# Icon examples here: http://www.bom.gov.au/info/forecast_icons.shtml

def xmldateparse(ds):
    return datetime.date(int(ds[0:4]), int(ds[5:7]), int(ds[8:10]))

def get_text(element, text_type):
    for member in element:
        if member.tag == 'text':
            if member.attrib["type"] == text_type:
                return member.text
    return None

def get_element(element, element_type):
    for member in element:
        if member.tag == 'element':
            if member.attrib["type"] == element_type:
                return member.text
    return None

def set_short_forecast(forecast_period, maxstat, minstat, forecast_stat, label=None):
    forecast = get_text(forecast_period, "precis")
    maxtemp = get_element(forecast_period, "air_temperature_maximum")
    mintemp = get_element(forecast_period, "air_temperature_minimum")
    icon_index = get_element(forecast_period, "forecast_icon_code")
    if label:
        set_statistic_data("weather", "rt", maxstat, int(maxtemp), label="Max")
    else:
        set_statistic_data("weather", "rt", maxstat, int(maxtemp))
    if mintemp is not None:
        if label:
            set_statistic_data("weather", "rt", minstat, int(mintemp), label="Min")
        else:
            set_statistic_data("weather", "rt", minstat, int(mintemp))
    else:
        clear_statistic_data("weather", "rt", minstat)
    icon = get_icon("weather_icon_scale", int(icon_index))
    set_statistic_data("weather", "rt", forecast_stat, forecast, icon_code=icon, label=label)
    return icon

def update_data(loader, verbosity=0):
    messages = update_forecasts(verbosity)
    update_current_temp()
    return messages

def update_current_temp():
    ftp = FTP('ftp2.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    buf = TemporaryFile()
    ftp.retrbinary('RETR IDN60920.xml', buf.write)
    ftp.quit()
    buf.seek(0)
    xml = ET.parse(buf)
    obs = xml.getroot()[1]
    if obs.tag != "observations":
        buf.close()
        raise LoaderException("XML Format error: Expected 'observations' Got '%s'" % obs.tag)
    for station in obs:
        if station.tag != "station":
            buf.close()
            raise LoaderException("XML Format error: Expected 'station' Got '%s'" % station.tag)
        if station.attrib["stn-name"] == "SYDNEY (OBSERVATORY HILL)":
            for level in station[0]:
                if level.tag != "level":
                    raise LoaderException("XML Format error: Expected 'level' Got '%s'" % station.tag)
                if level.attrib["type"] == "surface":
                    temp = get_element(level, "air_temperature")
                    temp = decimal.Decimal(temp)
                    set_statistic_data("weather", "rt", "current_temp", temp)
                    buf.close()
                    return
            buf.close()
            raise LoaderException("No surface observations data for Sydney available")
    buf.close()
    raise LoaderException("No observations data for Sydney available")

def update_forecasts(verbosity):
    messages = []

    # Forecasts
    ftp = FTP('ftp2.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    buf = TemporaryFile()
    ftp.retrbinary('RETR IDN10064.xml', buf.write)
    ftp.quit()
    buf.seek(0)
    xml = ET.parse(buf)
    forecasts = xml.getroot()[1]
    if forecasts.tag != "forecast":
        buf.close()
        raise LoaderException("XML Format error: Expected 'forecast' Got '%s'" % forecasts.tag)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    day2 = today + datetime.timedelta(days=2)
    day3 = today + datetime.timedelta(days=3)
    long_forecast = None
    long_forecast_icon = None
    for area in forecasts:
        if area.tag != "area":
            buf.close()
            raise LoaderException("XML Format error: Expected 'area' Got '%s'" % area.tag)
        if area.attrib["description"] != "Sydney":
            continue
        for forecast_period in area:
            day=xmldateparse(forecast_period.attrib["start-time-local"]) 
            if day == today:
                if area.attrib["type"] == "metropolitan":
                    long_forecast = get_text(forecast_period, "forecast")
                elif area.attrib["type"] == "location":
                    long_forecast_icon=set_short_forecast(forecast_period, "today_max", "today_min", "today_short_forecast")
            elif day == tomorrow:
                if area.attrib["type"] == "location":
                    set_short_forecast(forecast_period, "day_1_max", "day_1_min", "day_1_forecast", 
                                        label="Tomorrow")
            elif day == day2:
                if area.attrib["type"] == "location":
                    set_short_forecast(forecast_period, "day_2_max", "day_2_min", "day_2_forecast", 
                                        label=day2.strftime("%A"))
            elif day == day3:
                if area.attrib["type"] == "location":
                    set_short_forecast(forecast_period, "day_3_max", "day_3_min", "day_3_forecast",
                                        label=day3.strftime("%A"))
            else:
                continue
    if long_forecast and long_forecast_icon:
        if verbosity >= 3:
            messages.append("Long forecast %d characters: <%s>" % (
                                        len(long_forecast),
                                        long_forecast))
        set_statistic_data("weather", "rt", "today_long_forecast", long_forecast, icon_code=long_forecast_icon)
    else:
        clear_statistic_data("weather", "rt", "today_long_forecast")
    buf.close()
    stat = get_statistic("weather", "rt", "today_max").get_data().intval
    climate_delta = decimal.Decimal(stat) - decimal.Decimal(monthly_avg_temp[today.month-1])
    trend = int(climate_delta.compare(decimal.Decimal("0")))
    set_statistic_data("weather", "rt", "seasonal_average", climate_delta, trend=trend)
    return messages
