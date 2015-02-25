import datetime
import decimal
import random
import pytz
import httplib
from HTMLParser import HTMLParser, HTMLParseError

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code

# Refresh every two hours
refresh_rate = 60 * 60 * 2

class WaterLevelHtmlParser(HTMLParser):
    def __init__(self, messages, verbosity, *args, **kwargs):
        self.messages = messages
        self.verbosity = verbosity
        self.div_stack = []
        self.span_stack = []
        self.pc = None
        self.net_change = None
        self.main_stats_written = False
        self.dams_done = []
        # HTMLParser is not a new-style class, so you can't use super(!)
        HTMLParser.__init__(self, *args, **kwargs)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.span_stack:
                raise HTMLParseError("div nested in span")
            self.div_stack.append(attrs)
        elif tag == "span":
            self.span_stack.append(attrs)
    def handle_endtag(self, tag):
        if tag == "div":
            if self.span_stack:
                raise HTMLParseError("Span still open at end of div")
            ending = self.div_stack.pop()
        elif tag == "span":
            if not self.span_stack:
                raise HTMLParseError("Unmatched /span tag")
            self.span_stack.pop()
    def handle_data(self, data):
        if self.div_stack_contains("id", "bom-sydney-xml-feed"):
            if self.current_div().get("class") == "percent-full":
                self.pc = float(data)
            elif self.current_div().get("class") == "net-change":
                self.net_change = float(data)
            if not self.main_stats_written and self.pc is not None and self.net_change is not None:
                if self.pc is None:
                    raise HTMLParseError("All dams average not found")
                last_week = self.pc + self.net_change
                if abs(self.net_change) < 0.00001:
                    trend = 0
                elif self.net_change > 0.0:
                    trend = 1
                else:
                    trend = -1
                tlc = self.tlc(self.pc)
                tlc_lastweek = self.tlc(last_week)
                set_statistic_data("dam", "day", "all_dams_avg", 
                                    self.pc,
                                    trend = trend,
                                    traffic_light_code = tlc)
                set_statistic_data("dam", "day", "all_dams_last_week", 
                                    last_week,
                                    traffic_light_code = tlc_lastweek)
                self.main_stats_written = True
                self.pc = None
                self.net_change = None
                if self.verbosity >= 3:
                    self.messages.append("Updated total average dam levels")
        elif self.div_stack_contains("id", "bom-individual-xml-feed") and self.div_stack_contains("id", "dams"):
            dam = self.outer_div().get("class")
            if dam in ("warragamba", "avon", "cataract", "cordeaux"):
                if self.current_div().get("class") == "curr-pc":
                    self.pc = float(data)
                elif self.current_div().get("class") == "lw-pc-change":
                    self.net_change = float(data)
                if dam not in self.dams_done and self.net_change is not None and self.pc is not None:
                    if abs(self.net_change) < 0.00001:
                        trend = 0
                    elif self.net_change > 0.0:
                        trend = 1
                    else:
                        trend = -1
                    tlc = self.tlc(self.pc)
                    set_statistic_data("dam", "day", dam, 
                                    self.pc,
                                    trend = trend,
                                    traffic_light_code = tlc)
                    self.dams_done.append(dam)
                    self.pc = None
                    self.net_change = None
                    if self.verbosity >= 3:
                        self.messages.append("Updated dam levels for %s Dam" % dam.title())
    def tlc(self, percentage):
        if percentage <= 25.0:
            return "bad"
        elif percentage <= 40.0:
            return "poor"
        else:
            return "good"
    def current_div(self):
        frame = len(self.div_stack)
        if frame > 0:
            return self.div_stack[frame - 1]
        else:
            return None
    def current_span(self):
        frame = len(self.span_stack)
        if frame > 0:
            return self.span_stack[frame - 1]
        else:
            return None
    def outer_div(self, depth=1):
        frame = len(self.div_stack)
        frame = frame - depth
        if frame > 0:
            return self.div_stack[frame - 1]
        else:
            return None
    def div_stack_contains(self, key, value):
        for f in self.div_stack:
            if f.get(key) == value:
                return True
        return False

def get_damdata(messages, verbosity=0):
    http = httplib.HTTPConnection("www.sca.nsw.gov.au")
    http.request("GET", "http://www.sca.nsw.gov.au/water/dam-levels")
    resp = http.getresponse()
    parser = WaterLevelHtmlParser(messages, verbosity)
    parser.feed(resp.read())
    http.close()
    return parser.messages

def update_data(loader, verbosity=0):
    messages = []
    try:
        messages = get_damdata(messages, verbosity)
    except HTMLParseError, e:
        raise LoaderException("Error parsing dam levels website: %s" % unicode(e))
    return messages

