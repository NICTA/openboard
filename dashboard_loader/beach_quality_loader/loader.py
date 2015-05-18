import time
import datetime
import pytz
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

from beach_quality_loader.models import BeachSummaryHistory, CurrentBeachRating

# Refresh data every 3 hours
refresh_rate = 60*60*3

def update_data(loader, verbosity=0):
    messages = []
    messages = call_in_transaction(refresh_data,loader, verbosity)
    return messages

def refresh_data(loader, verbosity=0):
    messages = []
    clear_statistic_list("beaches", "nsw", "day", "highlight_beach")
    http = httplib.HTTPConnection("www.environment.nsw.gov.au")
    if verbosity > 5:
        csv_headings()
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/OceanBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.SYDNEY_OCEAN, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/SydneyBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.SYDNEY_HARBOUR, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/BotanyBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.BOTANY_BAY, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Botany Bay beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/PittwaterBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.PITTWATER, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Pittwater beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/CentralCoastBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.CENTRAL_COAST, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Central Coast beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/IllawarraBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.ILLAWARRA, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Illawarra beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/HunterBulletin.xml")
        resp = http.getresponse()
        messages.extend(process_xml(BeachSummaryHistory.HUNTER, resp, verbosity=verbosity))
    except LoaderException, e:
        messages.append("Error updating Hunter beach data: %s" % unicode(e))
    http.close()
    try:
        messages.extend(update_stats())
    except LoaderException, e:
        messages.append("Error updating widget stats: %s" % unicode(e))
    return messages

def update_stats():
    messages = []
    today = datetime.date.today()
    start_of_year = datetime.datetime(today.year, 1, 1)
    messages.extend(update_summary_stat(
            "beaches", "nsw", "day", "all_ocean_beaches",
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches(),
                day=today),
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches(),
                day=day_before(today))
            ))
    messages.extend(update_summary_stat(
            "beaches", "nsw", "day", "all_ocean_ytd",
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches(),
                day__gte=start_of_year,
                day__lte=today
                )
            ))
    for region in BeachSummaryHistory.regions:
        messages.extend(update_summary_stat(
                "beaches", "nsw", "day", "region_%s" % region,
                BeachSummaryHistory.objects.filter(
                    region=region,
                    day=today
                    )
                ))
    messages.append("Statistics updated") 
    return messages

def day_before(d):
    dt = datetime.datetime.combine(d, datetime.time(0,0,0))
    dt -= datetime.timedelta(days=1)
    return dt.date()

def update_summary_stat(widget_url, widget_location_url, widget_freq_url, statistic_url,
        beachsummary_set, trend_cmp_set=None):
    messages = []
    if not beachsummary_set:
        return ["Beach summary set for widget %s(%s,%s) is empty" % (widget_url, widget_location_url, widget_freq_url)]
    total_likely = 0
    total_possible = 0
    total_unlikely = 0
    for bs in beachsummary_set:
        total_likely += bs.num_pollution_likely
        total_possible += bs.num_pollution_possible
        total_unlikely += bs.num_pollution_unlikely
    (value, tlc) = summarise_quality(total_likely, total_possible, total_unlikely)
    if trend_cmp_set is None:
        trend = None
    elif trend_cmp_set:
        total_likely = 0
        total_possible = 0
        total_unlikely = 0
        for bs in trend_cmp_set:
            total_likely += bs.num_pollution_likely
            total_possible += bs.num_pollution_possible
            total_unlikely += bs.num_pollution_unlikely
        (trend_value, trend_tlc) = summarise_quality(total_likely, total_possible, total_unlikely)
        trend = value_cmp(trend_value, value) 
    else:
        messages.append("No past data to determine trend")
        trend = 0
    set_statistic_data(widget_url, widget_location_url, widget_freq_url, statistic_url, value,
                traffic_light_code = tlc, trend=trend)
    return messages

def value_cmp(old, new):
    if old == new:
        return 0
    elif old == "Poor":
        return 1
    elif old == "Good":
        return -1
    elif new == "Poor":
        return -1
    else:
        return 1

def summarise_quality(total_likely, total_possible, total_unlikely):
    total = float(total_likely + total_possible + total_unlikely)
    if total_likely/total > 0.2 or (total_possible + total_likely)/total > 0.7:
        return ("Poor", "bad")
    elif (total_possible + total_likely)/total > 0.4:
        return ("Fair", "poor")
    else:
        return ("Good", "good")

def process_xml(region, resp, verbosity=0):
    xml = ET.parse(resp)
    title = BeachSummaryHistory.regions[region]
    # dump_xml(region, xml)
    if verbosity > 5:
        dump_as_csv(region, xml)
    num_unlikely = 0
    num_possible = 0
    num_likely = 0
    sort_order = BeachSummaryHistory.sort_orders[region]
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
# print "Beach %s Advice: %s" % (beach_name, advice)
            beach.rating = beach.parse_advice(advice)
            beach.save()
            if beach.rating == beach.GOOD:
                val = "Good"
                tlc = "good"
                num_unlikely += 1
            elif beach.rating == beach.FAIR:
                val = "Fair"
                tlc = "poor"
                num_possible += 1
            else:
                num_likely += 1
                val = "Poor"
                tlc = "bad"
            add_statistic_list_item("beaches", "nsw", "day", "highlight_beach",
                        val, sort_order,
                        label=beach.beach_name,
                        traffic_light_code=tlc)
        sort_order += 10
    try:
        summary = BeachSummaryHistory.objects.get(region=region, day=datetime.date.today())
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

def csv_headings():
    print "Advice Rank,Region,Weather,Winds,Rainfall,Air Temp(degC),Ocean Temp(degC),Swell,High Tide,Low Tide,Beach,Latitude,Longitude,BSG,Advice,Star Rating"

def dump_as_csv(region, xml):
    region = csv_escape(BeachSummaryHistory.regions[region])
    for elem in xml.getroot()[0]:
        if elem.tag.endswith( '}data'):
            data = elem
            for d in data:
                if d.tag.endswith('}weather'):
                    weather = csv_escape(d.text)
                elif d.tag.endswith('}winds'):
                    winds = csv_escape(d.text)
                elif d.tag.endswith('}rainfall'):
                    rainfall = csv_escape(d.text)
                elif d.tag.endswith('}airTemp'):
                    airtemp = csv_escape(d.text)
                elif d.tag.endswith('}oceanTemp'):
                    oceantemp = csv_escape(d.text)
                elif d.tag.endswith('}swell'):
                    swell = csv_escape(d.text)
                elif d.tag.endswith('}highTide'):
                    hitide = csv_escape(d.text)
                elif d.tag.endswith('}lowTide'):
                    lotide = csv_escape(d.text)
            continue
        elif elem.tag == 'item':
            item = elem
            for i in item:
                if i.tag == 'title':
                    beach = csv_escape(i.text)
                elif i.tag.endswith('}data'):
                    data = i
                    for d in data:
                        if d.tag.endswith('}advice'):
                            advice = csv_escape(d.text)
                        elif d.tag.endswith('}bsg'):
                            bsg = csv_escape(d.text)
                        elif d.tag.endswith('}starRating'):
                            star_rating = csv_escape(len(d.text.strip()))
                        elif d.tag.endswith('}latitude'):
                            lat = csv_escape(d.text)
                        elif d.tag.endswith('}longitude'):
                            lng = csv_escape(d.text)
            if "unlikely" in advice:
                advice_rank = "3"
            elif "possible" in advice:
                advice_rank = "2"
            else:
                advice_rank = "1"
            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                advice_rank, region,weather,winds,rainfall,airtemp,oceantemp,
                swell,hitide,lotide,
                beach,lat,lng,bsg,advice,star_rating
            )

def csv_escape(input):
    uin = unicode(input).strip()
    uout = None
    if '"' in uin:
        uout = re.sub(r'"', '""', uin)
    if ',' in uin and not uout:
        uout = uin
    if uout:
        return '"' + uout + '"'
    else:
        return uin

