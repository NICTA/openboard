import time
import datetime
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

from beach_quality_loader.models import BeachSummaryHistory, CurrentBeachRating

# Refresh data every 3 hours
refresh_rate = 60*60*3

def update_data(loader, verbosity=0):
    messages = []
    http = httplib.HTTPConnection("www.environment.nsw.gov.au")
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/OceanBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.SYDNEY_OCEAN, resp))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/SydneyBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.SYDNEY_HARBOUR, resp))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/BotanyBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.BOTANY_BAY, resp))
    except LoaderException, e:
        messages.append("Error updating Botany Bay beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/PittwaterBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.PITTWATER, resp))
    except LoaderException, e:
        messages.append("Error updating Pittwater beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/CentralCoastBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.CENTRAL_COAST, resp))
    except LoaderException, e:
        messages.append("Error updating Central Coast beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/IllawarraBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.ILLAWARRA, resp))
    except LoaderException, e:
        messages.append("Error updating Illawarra beach data: %s" % unicode(e))
    http.close()
    return messages

def process_xml(region, resp):
    xml = ET.parse(resp)
    title = BeachSummaryHistory.regions[region]
    # dump_xml(region, xml)
    num_unlikely = 0
    num_possible = 0
    num_likely = 0
    for elem in xml.getroot()[0]:
        if elem.tag == 'item':
            beach_name = None
            advice = None
            item = elem
            for i in item:
                if i.tag == 'title':
                    beach_name = i.text
                elif i.tag.endswith('}data'):
                    data = i
                    for d in data:
                        if d.tag.endswith('}advice'):
                            advice = d.text.strip()
            if not beach_name: 
                raise LoaderException("Parse error: Beach with no name")
            if not advice:
                raise LoaderException("Parse error: Beach %s has no advice" % beach_name)
            try:
                beach = CurrentBeachRating.objects.get(region=region, beach_name = beach_name)
            except CurrentBeachRating.DoesNotExist:
                beach = CurrentBeachRating(region=region, beach_name=beach_name)
            beach.rating = beach.parse_advice(advice)
            beach.save()
            if beach.rating == beach.GOOD:
                num_unlikely += 1
            elif beach.rating == beach.FAIR:
                num_possible += 1
            else:
                num_likely += 1
    try:
        summary = BeachSummaryHistory.objects.get(region=region, day=datetime.datetime.today())
    except BeachSummaryHistory.DoesNotExist:
        summary = BeachSummaryHistory(region=region)
    if num_unlikely + num_possible + num_likely == 0:
        raise LoaderException("No beaches found in RSS feed")
    summary.num_pollution_unlikely = num_unlikely
    summary.num_pollution_possible = num_possible
    summary.num_pollution_likely = num_likely
    summary.save()
    return ["Loaded data for %s beaches" % title]

def dump_xml(region, xml):
    title = BeachSummaryHistory.regions[region]
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

