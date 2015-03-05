import time
import datetime
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

# Refresh data every 3 hours
refresh_rate = 60*60*3

def update_data(loader, verbosity=0):
    messages = []
    http = httplib.HTTPConnection("www.environment.nsw.gov.au")
    http.request("GET", "http://www.environment.nsw.gov.au/beachapp/OceanBulletin.xml")
    resp = http.getresponse()
    process_xml("Oceans", resp)
    http.request("GET", "http://www.environment.nsw.gov.au/beachapp/SydneyBulletin.xml")
    resp = http.getresponse()
    process_xml("Sydney", resp)
    http.close()
    return messages

def process_xml(title, resp):
    xml = ET.parse(resp)
    print "%s:" % title
    for elem in xml.getroot()[0]:
        if elem.tag.endswith( '}data'):
            data = elem
            for d in data:
                if d.tag.endswith('}weather'):
                    print "Weather: %s" % d.text
                elif d.tag.endswith('}winds'):
                    print "Winds: %s" % d.text  
                elif d.tag.endswith('}rainfall'):
                    print "Rainfall: %s" % d.text  
                elif d.tag.endswith('}airTemp'):
                    print "Air Temp: %sdegC" % d.text  
                elif d.tag.endswith('}oceanTemp'):
                    print "Ocean Temp: %sdegC" % d.text  
                elif d.tag.endswith('}swell'):
                    print "Swell: %s" % d.text  
                elif d.tag.endswith('}highTide'):
                    print "High Tide: %s" % d.text  
                elif d.tag.endswith('}lowTide'):
                    print "Low Tide: %s" % d.text  
            print "-------------------------"
        elif elem.tag == 'item':
            item = elem
            for i in item:
                if i.tag == 'title':
                    print "Beach: %s" % i.text
                elif i.tag.endswith('}data'):
                    data = i
                    for d in data:
                        if d.tag.endswith('}advice'):
                            print "Advice: %s" % d.text.strip()
                        elif d.tag.endswith('}bsg'):
                            print "BSG: %s" % d.text  
                        elif d.tag.endswith('}starRating'):
                            print "Star Rating: %d" % len(d.text.strip())
                        elif d.tag.endswith('}latitude'):
                            print "lat: %s" % d.text  
                        elif d.tag.endswith('}longitude'):
                            print "long: %s" % d.text  
            print "-------------------------"
    print "======================================" 
