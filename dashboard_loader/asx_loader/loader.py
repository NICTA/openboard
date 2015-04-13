import decimal
import httplib
from HTMLParser import HTMLParser, HTMLParseError

from django.conf import settings

from dashboard_loader.loader_utils import set_statistic_data, call_in_transaction, clear_statistic_list, add_statistic_list_item

# Refresh every 100 seconds
refresh_rate = 100

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
                self.index_value = decimal.Decimal("".join(data.split(",")))
# set_statistic_data("asx", "nsw", "rt", "index", value)  
                if self.verbosity > 5:
                    print "Index: %s" % data
            if self.read_rt_percent:
                strval = data.strip("(%)")
                value = decimal.Decimal(strval)
                set_statistic_data("asx", "nsw", "rt", "movement", value)  
                if self.verbosity > 5:
                    print "RT percent move: %s" % data
                if self.index_value.is_zero():
                    trend = 0
                elif self.index_value.is_signed():
                    trend = -1
                else:
                    trend = 1
                set_statistic_data("asx", "nsw", "rt", "index", self.index_value, trend=trend)  
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

class StockQuote(object):
    def __init__(self, code, name=None, last_trade_price=None, percent=None,
                        is_neg=None):
        self.code = code
        self._name = name
        self.last_trade_price = last_trade_price
        self.percent = percent
        self._is_neg = None
        if is_neg:
            self._is_neg = True
    def set_percent(self, percent):
        self._percent = percent
        if percent is None:
            self._is_neg = None
        elif percent.is_signed() and not percent.is_zero():
            self._is_neg = True
        elif self._is_neg and not percent.is_zero():
            self._percent = self._percent.copy_negate()
        else:
            self._is_neg = False
    def get_percent(self):
        return self._percent
    percent = property(get_percent, set_percent)
    def set_is_neg(self, is_neg):
        if is_neg:
            self._is_neg = True
            if self._percent is not None and not self._percent.is_signed() and not self._percent.is_zero():
                self._percent = self._percent.copy_negate()
        else:
            self._is_neg = False
            if self._percent is not None and self._percent.is_signed():
                self._percent = self._percent.copy_negate()
    def get_is_neg(self):
        return self._is_neg
    is_neg = property(get_is_neg, set_is_neg)
    def set_name(self, name):
        if self._name:
            self._name += " " + name
        else:
            self._name = name
    def get_name(self):
        return self._name
    name = property(get_name, set_name)
    def trend(self):
        if self._percent.is_zero():
            return 0
        elif self._is_neg:
            return -1
        else:
            return 1

class ASXQuoteHtmlParser(HTMLParser):
    def __init__(self, messages, verbosity, *args, **kwargs):
        self.messages = messages
        self.verbosity = verbosity
        self.in_quotestab_div = False
        self.in_quotestab_tr = False
        self.in_quotestab_td = False
        self.in_quotepc_span = False
        self.in_quotepc_inner_span = False
        self.quotepc_isneg = False
        self.td_count = 0
        self.inlasttradeprice_span = False
        self.quote = None
        self.quotes = []
        HTMLParser.__init__(self, *args, **kwargs)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and attrs.get("id")=="yfitp" and attrs.get("class")=="yfitabsc":
            self.in_quotestab_div = True
        elif tag == "tr" and self.in_quotestab_div:
            self.in_quotestab_tr = True
            self.td_count = 0
        elif tag == "td" and self.in_quotestab_tr:
            self.td_count += 1
            self.in_quotestab_td = True
        elif tag == "span" and self.in_quotestab_td and self.td_count == 3 and attrs.get("id").startswith("yfs_l"):
            self.inlasttradeprice_span = True
        elif tag == "span" and self.in_quotestab_td and self.td_count == 4 and attrs.get("id").startswith("yfs_p"):
            self.in_quotepc_span = True
        elif tag == "span" and self.in_quotepc_span:
            self.in_quotepc_inner_span = True
            self.quotepc_isneg = attrs["class"].endswith("red")
        elif tag == "b" and self.in_quotepc_span:
            self.in_quotepc_inner_span = True
            self.quotepc_isneg = ("cc0000" in attrs["style"])
    def handle_endtag(self, tag):
        if tag == "div" and self.in_quotestab_div:
            self.in_quotestab_div = False
        elif tag == "tr" and self.in_quotestab_tr:
            self.in_quotestab_tr = False
            self.td_count = 0
            if self.quote:
                self.quotes.append(self.quote)
                if self.verbosity > 5:
                    print "%s(%s) %s, %s%%" % (self.quote.name,
                                                self.quote.code,
                                                unicode(self.quote.last_trade_price),
                                                unicode(self.quote.percent))
                                            
                self.quote = None
        elif tag == "td" and self.in_quotestab_td:
            self.in_quotestab_td = False
        elif tag == "span" and self.in_quotepc_inner_span:
            self.in_quotepc_inner_span = False
        elif tag == "b" and self.in_quotepc_inner_span:
            self.in_quotepc_inner_span = False
        elif tag == "span" and self.in_quotepc_span:
            self.in_quotepc_span = False
        elif tag == "span" and self.inlasttradeprice_span:
            self.inlasttradeprice_span = False
    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.in_quotestab_td:
                if self.td_count == 1:
                    if self.verbosity >= 5:
                        print "\tSymbol: %s" % data
                    self.quote = StockQuote(data)
                elif self.td_count == 2:
                    if self.verbosity >= 5:
                        print "\tName: %s" % data
                    self.quote.name = data
                elif self.td_count == 3 and self.inlasttradeprice_span:
                    val = decimal.Decimal(data)
                    if self.verbosity >= 5:
                        print "\tLast trade price: %s" % repr(val)
                    self.quote.last_trade_price = val
                elif self.td_count == 4 and self.in_quotepc_inner_span:
                    val = data.strip("(%)")
                    if self.quotepc_isneg:
                        val = "-" + val
                    val = decimal.Decimal(val)
                    if self.verbosity >= 5:
                        print "\tPercent Change: %s" % repr(val)
                    self.quote.percent = val
               
def update_data(loader, verbosity=0):
    messages = []
    try:
        if verbosity > 5:
            print "Getting ASX-200 data..."
        messages = call_in_transaction(get_asxdata,messages, verbosity)
        if verbosity > 2:
            messages.append("ASX-200 data updated")
        if verbosity > 5:
            print "Getting Active stock quote data..."
        messages = call_in_transaction(get_asxquotes, messages, verbosity)
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

def get_asxquotes(messages, verbosity):
    http = httplib.HTTPSConnection("au.finance.yahoo.com")
    http.request("GET", "https://au.finance.yahoo.com/actives?e=ax")
    resp = http.getresponse()
    parser = ASXQuoteHtmlParser(messages, verbosity)
    parser.feed(resp.read())
    http.close()
    if verbosity > 2:
        parser.messages.append("%d stock quotes found" % len(parser.quotes))
    if len(parser.quotes) > 0:
        clear_statistic_list("asx", "nsw", "rt", "stock_prices")
        sort_order = 10
        for q in parser.quotes[0:25]:
            add_statistic_list_item("asx", "nsw", "rt", "stock_prices",
                    q.last_trade_price, sort_order,
                    label = q.code,
                    trend = q.trend())
            sort_order += 10
    if verbosity > 1:
        parser.messages.append("%d stock quotes saved" % (len(parser.quotes[0:25])))
    return parser.messages

 
