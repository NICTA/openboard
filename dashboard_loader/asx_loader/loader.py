import decimal
import httplib
from HTMLParser import HTMLParser, HTMLParseError

from django.conf import settings

from dashboard_loader.loader_utils import set_statistic_data, call_in_transaction

# Refresh every 40 seconds
refresh_rate = 40

class ASXHtmlParser(HTMLParser):
    def __init__(self, messages, verbosity, *args, **kwargs):
        self.messages = messages
        self.verbosity = verbosity
        self.read_index = False
        self.read_rt_percent = False
        self.read_day_min = False
        self.read_day_max = False
        self.in_index_range_table = False
        self.in_last_row = False
        self.last_row_span_count = 0
        self.read_last_row_span = False
        HTMLParser.__init__(self, *args, **kwargs)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "span" and attrs.get("id") == "yfs_l10_^axjo":
            self.read_index = True
        elif tag == "span" and attrs.get("id") == "yfs_p20_^axjo":
            self.read_rt_percent = True
        elif tag == "table" and attrs.get("id") == "table2":
            self.in_index_range_table = True
        elif self.in_index_range_table and tag=="span" and attrs.get("id") == "yfs_g00_^axjo":
            self.read_day_min = True
        elif self.in_index_range_table and tag=="span" and attrs.get("id") == "yfs_h00_^axjo":
            self.read_day_max = True
        elif self.in_index_range_table and tag=="tr" and attrs.get("class") == "end":
            self.in_last_row = True
        elif self.in_last_row and tag == "span":
            self.read_last_row_span = True
            self.last_row_span_count += 1
    def handle_endtag(self, tag):
        if tag == "span":
            if self.read_index:
                self.read_index = False
            if self.read_rt_percent:
                self.read_rt_percent = False
            if self.read_day_min:
                self.read_day_min = False
            if self.read_day_max:
                self.read_day_max = False
            if self.read_last_row_span:
                self.read_last_row_span = False
        if tag == "table" and self.in_index_range_table:
            self.in_index_range_table = False
        if tag == "tr" and self.in_last_row:
            self.in_last_row = False
    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.read_index:
                value = decimal.Decimal("".join(data.split(",")))
                set_statistic_data("asx", "nsw", "rt", "index", value)  
                if self.verbosity > 5:
                    print "Index: %s" % data
            if self.read_rt_percent:
                strval = data.strip("(%)")
                value = decimal.Decimal(strval)
                set_statistic_data("asx", "nsw", "rt", "movement", value)  
                if self.verbosity > 5:
                    print "RT percent move: %s" % data
            if self.read_day_min:
                value = decimal.Decimal("".join(data.split(",")))
                set_statistic_data("asx", "nsw", "rt", "today_min", value)  
                if self.verbosity > 5:
                    print "Day Min: %s" % data
            if self.read_day_max:
                value = decimal.Decimal("".join(data.split(",")))
                set_statistic_data("asx", "nsw", "rt", "today_max", value)  
                if self.verbosity > 5:
                    print "Day Max: %s" % data
            if self.read_last_row_span:
                value = decimal.Decimal("".join(data.split(",")))
                if self.last_row_span_count == 1:
                    set_statistic_data("asx", "nsw", "rt", "yr_min", value)  
                    if self.verbosity > 5:
                        print "52wk Min: %s" % data
                else:
                    set_statistic_data("asx", "nsw", "rt", "yr_max", value)  
                    if self.verbosity > 5:
                        print "52wk Max: %s" % data

def update_data(loader, verbosity=0):
    messages = []
    try:
        messages = call_in_transaction(get_asxdata,messages, verbosity)
    except HTMLParseError, e:
        raise LoaderException("Error parsing Yahoo! Finance website: %s" % unicode(e))
    return messages

def get_asxdata(messages, verbosity):
    http = httplib.HTTPSConnection("au.finance.yahoo.com")
    http.request("GET", "https://au.finance.yahoo.com/q?s=^AXJO")
    resp = http.getresponse()
    parser = ASXHtmlParser(messages, verbosity)
    parser.feed(resp.read())
    http.close()
    return parser.messages
