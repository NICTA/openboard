import datetime
import pytz
import httplib
import xml.etree.ElementTree as ET

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

# Refresh hourly
refresh_rate = 60*60

def update_data(loader, verbosity=0):
    messages = []
    messages.extend(call_in_transaction(update_fire_danger, loader, verbosity))
    messages.append("Fire danger updated")
    return messages

class FireDanger(object):
    ratings = [
        { "level": "NONE", "rating": "None", "tlc": "none" },
        { "level": "LOW MODERATE", "rating": "Low-Moderate", "tlc": "low_moderate" },
        { "level": "HIGH", "rating": "High", "tlc": "high" },
        { "level": "VERY HIGH", "rating": "Very High", "tlc": "very_high" },
        { "level": "SEVERE", "rating": "Severe", "tlc": "severe" },
        { "level": "EXTREME", "rating": "Extreme", "tlc": "extreme" },
        { "level": "CATASTROPHIC", "rating": "Catastrophic", "tlc": "catastrophic" },
    ]
    def __init__(self, region, rating, fireban):
        self.region = region
        self.fireban = fireban
        for i in range(0,len(self.ratings)):
            if self.ratings[i]["level"] == rating:
                self._rating = i
                return
            if self.ratings[i]["rating"] == rating:
                self._rating = i
                return
        raise LoaderException("Unrecognised fire rating: %s" % rating)
    def tlc(self):
        return self.ratings[self._rating]["tlc"]
    def rating(self):
        if self.fireban:
            return "Total Fire Ban"
        else:
            return self.ratings[self._rating]["rating"]
    def __cmp__(self, other):
        if self._rating < other._rating:
            return -1
        elif self._rating > other._rating:
            return 1
        else:
            return 0

def update_fire_danger(loader, verbosity=0):
    messages = []
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    http = httplib.HTTPConnection("www.rfs.nsw.gov.au")
    http.request("GET", "http://www.rfs.nsw.gov.au/feeds/fdrToban.xml")
    xml = ET.parse(http.getresponse())
    expand_ratings = []
    for district in xml.getroot():
        region = None
        rating = None
        fireban = None
        for elem in district:
            if elem.tag == 'Name':
                region = elem.text
            elif elem.tag == 'DangerLevelToday':
                rating = elem.text
            elif elem.tag == 'FirebanToday':
                fireban = (elem.text == 'Yes')
        if rating is None:
            continue
        if region == "Greater Sydney Region":
            region = "Greater Sydney"
        elif region == "Illawarra/Shoalhaven":
            region = "Illawarra"
        elif region == "ACT":
            continue
        elif region == "Upper Central West Plains":
            region = "Upper C.W. Plains"
        elif region == "Lower Central West Plains":
            region = "Lower C.W. Plains"
        fd = FireDanger(region, rating, fireban)
        expand_ratings.append(fd)
    expand_ratings.sort(reverse=True)
    sort_order = 10
    clear_statistic_list("fire", "nsw", "day", "rating_list_main")
    clear_statistic_list("fire", "nsw", "day", "rating_list_expansion")
    for fd in expand_ratings:
        add_statistic_list_item("fire", "nsw", "day", "rating_list_main", fd.rating(), sort_order,
                    label=fd.region, traffic_light_code=fd.tlc())
        add_statistic_list_item("fire", "nsw", "day", "rating_list_expansion", fd.rating(), sort_order,
                    label=fd.region, traffic_light_code=fd.tlc())
        sort_order += 10
    loader.save()
    return messages

