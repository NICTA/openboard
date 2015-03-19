import time
import datetime
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

from beach_quality_loader.models import BeachSummaryHistory, CurrentBeachRating

# Refresh data every 90 minutes
refresh_rate = 60*90

def update_data(loader, verbosity=0):
    messages = []
    http = httplib.HTTPConnection("www.sydneytrains.info")
    http.request("GET", "http://www.sydneytrains.info/rss/feeds/serviceupdates.xml")
    resp = http.getresponse()
    if verbosity > 5:
        print resp.read()
    interruptions = process_interruptions(resp, messages)
    if verbosity >= 3:
        messages.append("Processed service interruptions")
    http.request("GET", "http://www.sydneytrains.info/rss/feeds/trackwork.xml")
    if verbosity > 5:
        print "----------------"
    resp = http.getresponse()
    if verbosity > 5:
        print resp.read()
    trackwork = process_trackwork(resp, messages)
    interruptions["all"].extend(trackwork["all"])
    interruptions["syd"].extend(trackwork["syd"])
    messages.append("Processed trackwork")
    http.close()
    load_interruptions("train_service_interrupt", "syd", interruptions["syd"])
    load_interruptions("train_service_interrupt", "nsw", interruptions["all"])
    return messages

def load_interruptions(widget, location_url, interruptions):
    clear_statistic_list(widget, location_url, "rt", "interruptions")
    sort_order=10
    for i in interruptions:
        add_statistic_list_item(widget, location_url, "rt", "interruptions",
                i["text"], sort_order, traffic_light_code=i["tlc"], url=i["link"])
        sort_order += 10

def process_trackwork(resp, messages):
    xml = ET.parse(resp)
    syd_current = 0
    all_current = 0
    syd_scheduled = 0
    all_scheduled = 0
    trackwork = { "all": [], "syd": [] }
    for item in xml.getroot()[0]:
        if item.tag != 'item':
            continue
        title = None
        link = None
        description = None
        for elem in item:
            if elem.tag == 'title':
                title = elem.text
            elif elem.tag == 'link':
                link = elem.text 
            elif elem.tag == 'description':
                description = elem.text
        bits = title.split(" - ")
        if len(bits) < 2:
            messages.append("Cannot parse trackwork title: %s" % title)
            continue
        line = bits[0].strip()
        (start_date, end_date) = parse_dates(bits[1].split(" to "))
        is_current = check_is_current(start_date, end_date)
        if is_current:
            is_scheduled = False
        else:
            is_scheduled = check_is_scheduled(start_date, end_date)
        if re.search("T[1-9]", line):
            is_syd = True
        elif "South West Rail Link" in line:
            is_syd = True
        else:
            is_syd = False
        if is_current:
            if is_syd:  
                syd_current += 1
            all_current += 1
            interruption = {
                    "text": description,
                    "link": link,
                    "tlc": "bad"
            }
            trackwork["all"].append(interruption)
            if is_syd:  
                trackwork["syd"].append(interruption)
        elif is_scheduled:
            if is_syd:  
                syd_scheduled += 1
            all_scheduled += 1
            interruption = {
                    "text": description,
                    "link": link,
                    "tlc": "poor"
            }
            trackwork["all"].append(interruption)
            if is_syd:  
                trackwork["syd"].append(interruption)
    syd_current_tlc = zerogood_tlc(syd_current, 3)
    all_current_tlc = zerogood_tlc(all_current, 3)
    set_statistic_data("train_service_interrupt", "syd", "rt", "current_trackwork",
                        syd_current, traffic_light_code = syd_current_tlc)
    set_statistic_data("train_service_interrupt", "nsw", "rt", "current_trackwork",
                        all_current, traffic_light_code = all_current_tlc)
    set_statistic_data("train_service_interrupt", "syd", "rt", "sched_overnight_trackwork",
                        syd_scheduled, traffic_light_code = "good")
    set_statistic_data("train_service_interrupt", "nsw", "rt", "sched_overnight_trackwork",
                        all_scheduled, traffic_light_code = "good")
    interruption = {
        "text": "No trackworks today",
        "tlc": "good",
        "link": "http://www.sydneytrains.info/service_updates/trackwork/"
    }
    if not trackwork["syd"]:
        trackwork["syd"].append(interruption)
    if not trackwork["all"]:
        trackwork["all"].append(interruption)
    return trackwork

def check_is_current(start_date, end_date):
    now = datetime.datetime.now()
    return start_date >= now and end_date <= now

def check_is_scheduled(start_date, end_date):
    now = datetime.datetime.now()
    today = datetime.date.today()
    deadline = datetime.datetime.combine(today, datetime.time(20,30,0))
    return start_date.date() == today and end_date >= now and start_date >= deadline

def parse_dates(dates):
    return (parse_date(dates[0].strip()), parse_date(dates[1].strip()))

def parse_date(ds):
    return datetime.datetime.strptime(ds, "%d/%m/%y %H:%M")

def process_interruptions(resp, messages):
    xml = ET.parse(resp)
    syd_delays = 0
    syd_cancellations = 0
    all_delays = 0
    all_cancellations = 0
    interruptions = { "all": [], "syd": [] }
    for item in xml.getroot()[0]:
        if item.tag != 'item':
            continue
        title = None
        link = None
        description = None
        for elem in item:
            if elem.tag == 'title':
                title = elem.text
            elif elem.tag == 'link':
                link = elem.text 
            elif elem.tag == 'description':
                description = elem.text
        if title == 'Good service':
            set_statistic_data("train_service_interrupt", "syd", "rt", "delays",
                                0, traffic_light_code = "good")
            set_statistic_data("train_service_interrupt", "syd", "rt", "cancellations",
                                0, traffic_light_code = "good")
            set_statistic_data("train_service_interrupt", "nsw", "rt", "delays",
                                0, traffic_light_code = "good")
            set_statistic_data("train_service_interrupt", "nsw", "rt", "cancellations",
                                0, traffic_light_code = "good")
            return {
                "all": [{
                    "text": title,
                    "tlc": "good",
                    "link": link
                }],
                "syd": [{
                    "text": title,
                    "tlc": "good",
                    "link": link
                }]
            }
        bits = title.split(" - ")
        if len(bits) != 2:
            raise LoaderException("Cannot parse item title: %s" % title)
        if re.search("T[1-9]", title):
            is_syd = True
        elif "South West Rail Link" in title:
            is_syd = True
        else:
            is_syd = False
        if bits[1].strip() == "Delays":
            if is_syd:
                syd_delays += 1
            all_delays += 1
            interruption = { "text": description,
                    "link": link,
                    "tlc": "poor"
            }
            interruptions["all"].append(interruption)
            if is_syd:
                interruptions["syd"].append(interruption)
        else:
            if is_syd:
                syd_cancellations += 1
            all_cancellations += 1
            interruption = {
                    "text": description,
                    "link": link,
                    "tlc": "bad"
            }
            interruptions["all"].append(interruption)
            if is_syd:
                interruptions["syd"].append(interruption)
    syd_del_tlc = zerogood_tlc(syd_delays, 7)
    all_del_tlc = zerogood_tlc(all_delays, 7)
    syd_cx_tlc = zerogood_tlc(syd_cancellations, 3)
    all_cx_tlc = zerogood_tlc(all_cancellations, 3)
    set_statistic_data("train_service_interrupt", "syd", "rt", "delays",
                        syd_delays, traffic_light_code = syd_del_tlc)
    set_statistic_data("train_service_interrupt", "syd", "rt", "cancellations",
                        syd_cancellations, traffic_light_code = syd_cx_tlc)
    set_statistic_data("train_service_interrupt", "nsw", "rt", "delays",
                        all_delays, traffic_light_code = all_del_tlc)
    set_statistic_data("train_service_interrupt", "nsw", "rt", "cancellations",
                        all_cancellations, traffic_light_code = all_cx_tlc)
    return interruptions

def zerogood_tlc(i, bad_cutoff):
    if i == 0:
        return "good"
    elif i > bad_cutoff:
        return "bad"
    else:
        return "poor"
