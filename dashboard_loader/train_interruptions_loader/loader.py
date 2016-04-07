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

import time
import datetime
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import *

# Refresh data every 90 minutes
refresh_rate = 60*90

# Function called when the loader is run.
def update_data(loader, verbosity=0):
    return call_in_transaction(load_data, verbosity)

def load_data(verbosity):
    messages = []
    interruptions = process_interruptions(messages,verbosity)
    if verbosity >= 1:
        messages.append("Processed service interruptions")
    trackwork = process_trackworks(messages,verbosity)
    interruptions["all"].extend(trackwork["all"])
    interruptions["syd"].extend(trackwork["syd"])
    if verbosity >= 1:
        messages.append("Processed trackwork")
    load_interruptions("train_service_interrupt", "syd:rt", interruptions["syd"])
    load_interruptions("train_service_interrupt", "nsw:rt", interruptions["all"])
    return messages

def load_interruptions(widget, label, interruptions):
    clear_statistic_list(widget, label, "interruptions")
    sort_order=10
    for i in interruptions:
        add_statistic_list_item(widget, label, "interruptions",
                i["text"], sort_order, traffic_light_code=i["tlc"], url=i["link"])
        sort_order += 10

def process_trackworks(messages, verbosity):
    url = "http://www.sydneytrains.info/rss/feeds/trackwork.xml"
    env = {
        "syd_current": 0,
        "all_current": 0,
        "syd_scheduled": 0,
        "all_scheduled": 0,
        "trackwork": { 
            "all": [], 
            "syd": [] 
        }
    }
    messages.extend(load_rss(url, process_trackwork, env, verbosity))
    set_statistic_data("train_service_interrupt", "syd:rt", 
                    "current_trackwork", env["syd_current"])
    set_statistic_data("train_service_interrupt", "nsw:rt", 
                    "current_trackwork", env["all_current"])
    set_statistic_data("train_service_interrupt", "syd:rt", 
                    "sched_overnight_trackwork", env["syd_scheduled"])
    set_statistic_data("train_service_interrupt", "nsw:rt", 
                    "sched_overnight_trackwork", env["all_scheduled"])
    interruption = {
        "text": "No trackworks today",
        "tlc": "good",
        "link": "http://www.sydneytrains.info/service_updates/trackwork/"
    }
    if not env["trackwork"]["syd"]:
        env["trackwork"]["syd"].append(interruption)
    if not env["trackwork"]["all"]:
        env["trackwork"]["all"].append(interruption)
    return env["trackwork"]


def process_trackwork(item, env, verbosity):
    messages = []
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
        return messages
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
            env["syd_current"] += 1
        env["all_current"] += 1
        interruption = {
                "text": description,
                "link": link,
                "tlc": "bad"
        }
        env["trackwork"]["all"].append(interruption)
        if is_syd:  
            env["trackwork"]["syd"].append(interruption)
    elif is_scheduled:
        if is_syd:  
            env["syd_scheduled"] += 1
        env["all_scheduled"] += 1
        interruption = {
                "text": description,
                "link": link,
                "tlc": "poor"
        }
        env["trackwork"]["all"].append(interruption)
        if is_syd:  
            env["trackwork"]["syd"].append(interruption)
    return messages

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

def process_interruptions(messages, verbosity):
    url = "http://www.sydneytrains.info/rss/feeds/serviceupdates.xml"
    env = {
        "syd_delays": 0,
        "syd_cancellations": 0,
        "all_delays": 0,
        "all_cancellations": 0,
        "interruptions": { 
            "all": [], 
            "syd": [] 
        }
    }
    messages.extend(load_rss(url, process_interruption, env, verbosity))
    set_statistic_data("train_service_interrupt", "syd:rt", 
                        "delays", env["syd_delays"])
    set_statistic_data("train_service_interrupt", "syd:rt", 
                        "cancellations", env["syd_cancellations"])
    set_statistic_data("train_service_interrupt", "nsw:rt", 
                        "delays", env["all_delays"])
    set_statistic_data("train_service_interrupt", "nsw:rt", 
                        "cancellations", env["all_cancellations"])
    interruption = {
        "text": "Good Service",
        "tlc": "good",
        "link": "http://www.sydneytrains.info/service_updates/service_interruptions/"
    }
    if not env["interruptions"]["syd"]:
        env["interruptions"]["syd"].append(interruption)
    if not env["interruptions"]["all"]:
        env["interruptions"]["all"].append(interruption)
    return env["interruptions"]

def process_interruption(item, env, verbosity):
    messages = []
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
        env["good_service"] = {
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
        return messages
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
            env["syd_delays"] += 1
        env["all_delays"] += 1
        interruption = { "text": description,
                "link": link,
                "tlc": "poor"
        }
        env["interruptions"]["all"].append(interruption)
        if is_syd:
            env["interruptions"]["syd"].append(interruption)
    else:
        if is_syd:
            env["syd_cancellations"] += 1
        env["all_cancellations"] += 1
        interruption = {
                "text": description,
                "link": link,
                "tlc": "bad"
        }
        env["interruptions"]["all"].append(interruption)
        if is_syd:
            env["interruptions"]["syd"].append(interruption)
    return messages

