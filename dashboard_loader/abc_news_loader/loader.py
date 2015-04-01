import time
import datetime
import pytz
import decimal
import re
import httplib
import xml.etree.ElementTree as ET
from pytz import FixedOffset

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

# Refresh data every 5 mins
refresh_rate = 60*5

def update_data(loader, verbosity=0):
    messages = []
    messages = refresh_data(loader, verbosity)
    return messages

def refresh_data(loader, verbosity=0):
    messages = []
    http = httplib.HTTPConnection("www.abc.net.au")
    try:
        http.request("GET", "/news/feed/52498/rss.xml")
        resp = http.getresponse()
        items = process_xml(resp, verbosity)
        messages.extend(call_in_transaction(load_items, items, verbosity))
    except LoaderException, e:
        messages.append("Error updating ABC News feed data: %s" % unicode(e))
    http.close()
    return messages

def load_items(items, verbosity=0):
    messages = []
    clear_statistic_list("news", "nsw", "rt", "headlines")
    items_loaded = 0
    for item in items:
        add_statistic_list_item("news", "nsw", "rt", "headlines", item["title"], (items_loaded + 1)*10,
                                    url=item["url"])
        items_loaded += 1
        if items_loaded >= 10:
            break
    messages.append("Added %d news items" % items_loaded)
    return messages

def process_xml(resp, verbosity=0):
    xml = ET.parse(resp)
    items = []
    for elem in xml.getroot()[0]:
        if elem.tag == 'item':
            items.append(parse_item(elem))
    if verbosity >= 5:
        all_cats = []
        for item in items:
            print "Title: %s" % item["title"]
            print "URL: %s" % item["url"]
            print "Pub date: %s" % item["published"].strftime("%a, %d %b %Y %H:%M:%S %z")
            print "Categories: %s" % ",".join(item["categories"])
            print "============================================================="
            print
            for cat in item["categories"]:
                if cat not in all_cats:
                    all_cats.append(cat)
        all_cats.sort()
        print "%d News items" % len(items)
        print "All Categories:"
        for cat in all_cats:
            print "\t%s" % cat
    return items

def parse_item(item):
    cats = []
    title = None
    datestr = None
    date = None
    link = None
    for elem in item:
        if elem.tag == "title":
            title = elem.text
        elif elem.tag == "link":
            link = elem.text
        elif elem.tag == "pubDate":
            date = parse_xmldate(elem.text)
        elif elem.tag == "category":
            cats.append(elem.text)
    return { "title": title,
             "url": link,
             "published": date,
             "categories": cats,
    }

def parse_xmldate(datestr):
    dtstr, sep, tzstr = datestr.rpartition(" ")
    naive_dt = datetime.datetime.strptime(dtstr, "%a, %d %b %Y %H:%M:%S")
    offset = int(tzstr[-4:-2])*60 + int(tzstr[-2:])
    if tzstr[0] == "-":
        offset = -offset
    return naive_dt.replace(tzinfo=FixedOffset(offset))
