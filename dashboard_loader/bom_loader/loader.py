import time
import datetime
import decimal
import re
from tempfile import TemporaryFile
from ftplib import FTP, error_perm, error_temp
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

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

    # IDN10064.xml - Forecasts
    # IDN60920.xml - NSW observations
# IDN65068:   Fire  Danger levels
# IDN65156:   Thunderstorm warning (txt)
# IDN20400:   Marine Wind Warnings
# IDN336*: Flood Warnings (TXT): "XXXX FLOOD WARNING"  (e.g. XXXX=MAJOR|MINOR|MODERATE|FINAL?) (txt)

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
    if maxtemp is not None:
        if label:
            set_statistic_data("weather", "rt", maxstat, int(maxtemp), label="Max")
        else:
            set_statistic_data("weather", "rt", maxstat, int(maxtemp))
    if mintemp is not None:
        if label:
            set_statistic_data("weather", "rt", minstat, int(mintemp), label="Min")
        else:
            set_statistic_data("weather", "rt", minstat, int(mintemp))
    icon = get_icon("weather_icon_scale", int(icon_index))
    set_statistic_data("weather", "rt", forecast_stat, forecast, icon_code=icon, label=label)
    return icon

def update_data(loader, verbosity=0):
    messages = []
    messages.extend(call_in_transaction(update_forecasts,verbosity))
    call_in_transaction(update_current_temp)
    messages.extend(call_in_transaction(update_warnings,verbosity))
# messages.extend(call_in_transaction(update_fire_danger,verbosity))
    return messages

class FireDanger(object):
    ratings = [
        { "rating": "None", "tlc": "none" },
        { "rating": "Low-Moderate", "tlc": "low_moderate" },
        { "rating": "High", "tlc": "high" },
        { "rating": "Very High", "tlc": "very_high" },
        { "rating": "Severe", "tlc": "severe" },
        { "rating": "Extreme", "tlc": "extreme" },
        { "rating": "Catastrophic", "tlc": "catastrophic" },
    ]
    def __init__(self, region, rating):
        self.region = region
        for i in range(0,len(self.ratings)):
            if self.ratings[i]["rating"] == rating:
                self._rating = i
                return
        raise LoaderException("Unrecognised fire rating: %s" % rating)
    def tlc(self):
        return self.ratings[self._rating]["tlc"]
    def rating(self):
        return self.ratings[self._rating]["rating"]
    def __cmp__(self, other):
        if self._rating < other._rating:
            return -1
        elif self._rating > other._rating:
            return 1
        else:
            return 0

def update_fire_danger(verbosity=0):
    messages = []
    ftp = FTP('ftp2.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    # IDN65068:   Fire  Danger levels
    buf = TemporaryFile()
    try:
        ftp.retrbinary('RETR IDN65068.xml', buf.write)
        buf.seek(0)
        if verbosity > 0:
            messages.append("Retreived fire danger ratings")
    except (error_perm, error_temp):
        buf.close()
        raise LoaderException("Fire Danger Ratings not found")
    ftp.quit()
    buf.seek(0)
    xml = ET.parse(buf)
    forecast = xml.getroot()[1]
    main_ratings = []
    expand_ratings = []
    for area in forecast:
        if area[0][0].attrib["type"] != "fire_danger":
            continue
        region = area.attrib["description"]
        if region == "Greater Sydney Region":
            region = "Greater Sydney"
        elif region == "Illawarra/Shoalhaven":
            region = "Illawarra"
        elif region == "The Australian Capital Territory":
            continue
        elif region == "Upper Central West Plains":
            region = "Upper C.W. Plains"
        elif region == "Lower Central West Plains":
            region = "Lower C.W. Plains"
        rating = area[0][0].text
        fd = FireDanger(region, rating)
        if region in ("Greater Sydney", "Illawarra", "Greater Hunter"):
            main_ratings.append(fd)
        else:
            expand_ratings.append(fd)
    buf.close()
    main_ratings.sort(reverse=True)
    expand_ratings.sort(reverse=True)
    clear_statistic_list("fire", "day", "rating_list_main")
    sort_order = 10
    for fd in main_ratings:
        add_statistic_list_item("fire", "day", "rating_list_main", fd.rating(), sort_order,
                    label=fd.region, traffic_light_code=fd.tlc())
        sort_order += 10
    clear_statistic_list("fire", "day", "rating_list_expansion")
    for fd in expand_ratings:
        add_statistic_list_item("fire", "day", "rating_list_expansion", fd.rating(), sort_order,
                    label=fd.region, traffic_light_code=fd.tlc())
        sort_order += 10
    return messages


class Severity(object):
    NONE = 0
    MINOR = 1
    MAJOR = 2
    STRONG = 3
    SEVERE = 4
    EXTREME = 5
    _sevs = [
        "None",
        "Minor",
        "Major",
        "Strong",
        "Severe",
        "Extreme",
    ]
    _tlcodes = [
        "No_warning",
        "minor",
        "major",
        "strong",
        "severe",
        "extreme",
    ]
    _sev_lookup = {
        "STR": STRONG,
        "MAJ": MAJOR,
        "MIN": MINOR,
        "SEV": SEVERE,
        "EXT": EXTREME,
    }
    def __init__(self, value = None):
        if value is None:
            self._index = 0
        elif isinstance(value, int):
            if value >= len(self._sevs) or value < 0:
                raise LoaderException("Invalid severity index: %d" % value)
            else:
                self._index = i
        else:
            self._index = -1
            for i in range(0, len(self._sevs)):
                if value.upper() == self._sevs[i].upper():
                    self._index = i
                    break
            if self._index < 0:
                if self._sev_lookup.get(value.upper()):
                    self._index = self._sev_lookup[value.upper()]
                else:
                    raise LoaderException("Invalid severity index: %s" % value)
    def tlc(self):
        return self._tlcodes[self._index]
    def escalate(self, other):
        if other > self:
            self._index = other._index
    def __unicode__(self):
        return self._sevs[self._index]
    def __str__(self):
        return self._sevs[self._index]
    def __cmp__(self, other):
        return cmp(self._index, other._index)

def trans_xml_warntype(wt):
    if wt == "MWW":
        return "Marine Wind Warning"
    else:
        return wt

def update_warnings(verbosity=0):
    messages = []
    warnings = []
    clear_statistic_list("emergency_warnings", "rt", "warnings_list")
    clear_statistic_list("emergency_warnings", "rt", "warnings_details_list")
    ftp = FTP('ftp2.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    # IDN20400.xml:   Marine Wind Warnings
    max_severity = Severity()
    try:
        buf = TemporaryFile()
        ftp.retrbinary('RETR IDN20400.xml', buf.write)
        buf.seek(0)
        xml = ET.parse(buf)
        product = xml.getroot()
        mwws = 0
        for elem in product:
            if elem.tag == 'warning':
                for subelem in elem:
                    if subelem.tag == 'area':
                        for fp in subelem:
                            detail = None
                            warning_type = None
                            priority = None
                            severity = None
                            phenomena = None
                            areas = None
                            if fp[0].tag == 'text' and fp[0].attrib["warning_summary"]:
                                detail = fp[0].text
                            elif fp[0].tag == 'hazard':
                                warning_type = fp[0].attrib["type"]
                                severity = Severity(fp[0].attrib["severity"])
                                for hazelem in fp[0]:
                                    if hazelem.tag == 'priority':
                                        priority = hazelem.text
                                    elif hazelem.tag == 'text' and hazelem.attrib["type"]=="warning_phenomena":
                                        phenomena = hazelem.text
                                    elif hazelem.tag == 'text' and hazelem.attrib["type"]=="warning_areas":
                                        areas = hazelem.text
                            warnings.append({
                                    "detail": detail,
                                    "warning_type": trans_xml_warntype(warning_type),
                                    "priority": priority,
                                    "severity": severity,
                                    "phenomena": phenomena,
                                    "areas": areas,
                                    })
                            max_severity.escalate(severity)
        buf.close()
        if verbosity > 0:
            messages.append("Retreived marine wind warnings")
    except (error_perm, error_temp):
        if verbosity > 0:
            messages.append("No marine wind warnings found")
    add_statistic_list_item("emergency_warnings", "rt", "warnings_list", 
                str(max_severity), 30,
                label="Marine Wind Warning", traffic_light_code=max_severity.tlc())
    # IDN336*: Flood Warnings (TXT): "XXXX FLOOD WARNING"  (e.g. XXXX=SEVERE|MAJOR|MINOR|MODERATE|FINAL?)
    files = []
    def append_file_name(filename):
        if filename.startswith("IDN366") and filename.endswith(".txt"):
            files.append(filename)
    ftp.retrlines('NLST', append_file_name)
    max_severity = Severity()
    for f in files:
        buf = TemporaryFile()
        ftp.retrbinary('RETR %s' % f, buf.write)
        buf.seek(0)
        for line in buf:
            if "FLOOD" in line:
                match = re.match("^(FINAL )?(.*) FLOOD (\S*) FOR (.*)$", line)
                if match:
                    severity = Severity(match.group(2))
                    warnings.append({
                            "detail": line.title(),
                            "warning_type": "Flood Warning",
                            "priority": match.group(3).title(),
                            "severity": severity,
                            "phenomena": (match.group(2) + " flood " + match.group(3)).title(),
                            "areas": match.group(4).title(),
                            })
                    max_severity.escalate(severity)
                else:
                    messages.append("Unparseable flood warning: %s" % line)
        buf.close()
        if verbosity > 0:
            messages.append("Retrieved flood warning: %s" % f)
    if not files and verbosity > 0:
        messages.append("No flood warnings retreived")
    add_statistic_list_item("emergency_warnings", "rt", "warnings_list", 
                str(max_severity), 10,
                label="Flood Warning", traffic_light_code=max_severity.tlc())
    # IDN65156:   Thunderstorm warning (txt)
    max_severity = Severity()
    try:
        buf = TemporaryFile()
        ftp.retrbinary('RETR IDN65156.txt', buf.write)
        buf.seek(0)
        tw = {}
        state = 0
        for line in buf:
            if state == 0 and "THUNDERSTORM" in line:
                match = re.match("^(.*) THUNDERSTORM (.*)$", line)
                if match:
                    tw["detail"] = line.title()
                    tw["severity"] = Severity(match.group(1))
                    tw["priority"] = match.group(2).title()
                    tw["warning_type"] = "Thunderstorm Warning"
                    state = 1
                else:
                    messages.append("Unparseable thunderstorm warning: %s" % line)
            elif state == 1 and line.startswith("for "):
                match = re.match("^for (.*)$", line)
                if match:
                    tw["detail"] += line.title()
                    tw["phenomena"] = match.group(1).title()
                    tw["areas"] = ""
                    state = 2
                else:
                    messages.append("Unparseable thunderstorm warning phenomena: %s" % line)
            elif state == 2 and line.startswith("For people in"):
                tw["detail"] += line.title() + " "
                state = 3
            elif state == 3:
                if line.strip():
                    tw["detail"] += line.title() + " "
                    tw["areas"] += line.title() + " "
                else:
                    break
        if tw.get("detail"):
            tw["detail"] = tw["detail"].strip()
            tw["areas"] = tw["areas"].strip()
            max_severity.escalate(tw["severity"])
            warnings.append(tw)
        buf.close()
        if verbosity > 0:
            messages.append("Retreived thunderstorm warnings")
    except (error_perm, error_temp):
        if verbosity > 0:
            messages.append("No thunderstorm warnings found")
    add_statistic_list_item("emergency_warnings", "rt", "warnings_list", 
                str(max_severity), 20,
                label="Thunderstorm Warning", traffic_light_code=max_severity.tlc())
    ftp.quit()
    sort_order = 10
    for w in warnings:
        add_statistic_list_item("emergency_warnings", "rt", "warnings_details_list", 
                        w["areas"], sort_order,
                        label=w["phenomena"], traffic_light_code=w["severity"].tlc())
        sort_order += 10
    return messages

def update_current_temp():
    ftp = FTP('ftp2.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    buf = TemporaryFile()
    # IDN60920.xml - NSW observations
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
    # IDN10064.xml - Forecasts
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
        # if verbosity >= 3:
        #    messages.append("Long forecast %d characters: <%s>" % (
        #                                len(long_forecast),
        #                                long_forecast))
        set_statistic_data("weather", "rt", "today_long_forecast", long_forecast, icon_code=long_forecast_icon)
    else:
        clear_statistic_data("weather", "rt", "today_long_forecast")
    buf.close()
    stat = get_statistic("weather", "rt", "today_max").get_data().intval
    climate_delta = decimal.Decimal(stat) - decimal.Decimal(monthly_avg_temp[today.month-1])
    trend = int(climate_delta.compare(decimal.Decimal("0")))
    set_statistic_data("weather", "rt", "seasonal_average", climate_delta, trend=trend)
    return messages
