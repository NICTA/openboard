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

import datetime
import decimal
import random
import pytz
import httplib
from HTMLParser import HTMLParser, HTMLParseError

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data, get_statistic, get_traffic_light_code, clear_statistic_list, add_statistic_list_item, call_in_transaction

from widget_def.models import Location

# Refresh every quarter hour
refresh_rate = 60 * 15

# Wrapper class for pollution ratings.
# N.B. Some of this functionality could be handled by the "MAP" type 
#      traffic light automation functionality that was not available when 
#      this code was written.
class PollutionRating(object):
    VERY_GOOD = 0
    GOOD = 1
    FAIR = 2
    POOR = 3
    VERY_POOR = 4
    HAZARDOUS = 5
    ratings = ["very_good", "good", "fair", "poor", "very_poor", "hazardous"]
    displays = ["Very Good", "Good", "Fair", "Poor", "Very Poor", "Hazardous"]
    def __init__(self, value):
        self.rating = self.translate_value(value)
    def translate_value(self, value):
        if value == "VERY GOOD":
            return self.VERY_GOOD
        elif value == "GOOD":
            return self.GOOD
        elif value == "FAIR":
            return self.FAIR
        elif value == "POOR":
            return self.POOR
        elif value == "VERY POOR":
            return self.VERY_POOR
        elif value == "HAZARDOUS":
            return self.HAZARDOUS
        else:
            raise HTMLParseError("Unknown rating value: %s" % value)
    def tlc(self):
        return self.ratings[self.rating]
    def display(self):
        return self.displays[self.rating]
    def __cmp__(self, other):
        return cmp(self.rating, other.rating)

# HTML Parser.
# Includes code which writes widget data to database
class AirPollutionHtmlParser(HTMLParser):
    def __init__(self, messages, verbosity, *args, **kwargs):
        self.messages = messages
        self.verbosity = verbosity
        self.tag_stack = []
        self.in_main_table_row = False
        self.this_row_ratings = False
        self.read_row_text = False
        self.last_row_texts = []
        self.row_texts = []
        self.row_text = []
        self.level_2_table_number = 0
        self.sort_order = 20
        self.sydney_worst = PollutionRating("VERY GOOD")
        self.in_syd_forecast_table = False
        self.now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        # HTMLParser is not a new-style class, so you can't use super(!)
        HTMLParser.__init__(self, *args, **kwargs)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tag_stack.append(tag)
        if tag == "table" and self.tables_instack() == 2:
            self.level_2_table_number += 1 
            if self.level_2_table_number == 2:
                self.in_syd_forecast_table = True
        elif tag == "tr" and self.tables_instack() == 2 and self.level_2_table_number == 1:
            self.in_main_table_row = True
            self.this_row_ratings = False
            self.last_row_texts = self.row_texts
            self.row_texts = []
        elif tag == "td" and self.tables_instack() == 2 and self.in_main_table_row:
            if not attrs.get("colspan"):
                self.read_row_text = True
        elif tag == "td" and self.in_syd_forecast_table:
            self.row_text = []
    def handle_endtag(self, tag):
        popped_ok = False
        while self.tag_stack:
            if tag == self.tag_stack.pop():
                popped_ok = True
                break
        if not popped_ok:
            raise HTMLParseError("Unmatched end tag: %s" % tag)
        if tag == "td" and self.tables_instack() == 2 and self.in_main_table_row:
            if self.read_row_text:
                self.read_row_text = False
                self.row_texts.append(" ".join(self.row_text))
                self.row_text = []
        elif tag == "tr" and self.tables_instack()==2 and self.in_main_table_row:
            self.in_main_table_row = False
            if self.this_row_ratings:
                for region, rating_val in zip(self.last_row_texts, self.row_texts):
                    rating=PollutionRating(rating_val)
                    if "Sydney" in region:
                        add_statistic_list_item("air_pollution", "syd", "rt", "regions", rating.display(), self.sort_order,
                                    label=region, traffic_light_code=rating.tlc())
                        add_statistic_list_item("air_pollution", "syd", "rt", "region_1", rating.display(), self.sort_order,
                                    label=region, traffic_light_code=rating.tlc())
                        if rating > self.sydney_worst:
                            self.sydney_worst = rating
                    else:
                        add_statistic_list_item("air_pollution", "nsw", "rt", "regions", rating.display(), self.sort_order,
                                    label=region, traffic_light_code=rating.tlc())
                        add_statistic_list_item("air_pollution", "nsw", "rt", "region_1", rating.display(), self.sort_order,
                                    label=region, traffic_light_code=rating.tlc())
                    self.sort_order += 10
        elif tag == "table" and self.tables_instack() == 1 and self.level_2_table_number == 1:
            add_statistic_list_item("air_pollution", "nsw", "rt", "regions", self.sydney_worst.display(), 10,
                        label="Sydney", traffic_light_code=self.sydney_worst.tlc())
            add_statistic_list_item("air_pollution", "nsw", "rt", "region_1", self.sydney_worst.display(), 10,
                        label="Sydney", traffic_light_code=self.sydney_worst.tlc())
        elif tag == "table" and self.tables_instack() == 1 and self.level_2_table_number == 2:
            self.in_syd_forecast_table = False
        elif tag == "td" and self.in_syd_forecast_table:
            if self.row_text:
                val = " ".join(self.row_text)
                try:
                    rating = PollutionRating(val)
                    set_statistic_data("air_pollution", "nsw", "rt", "sydney_forecast", rating.display(),
                                            traffic_light_code = rating.tlc())
                    set_statistic_data("air_pollution", "syd", "rt", "sydney_forecast", rating.display(),
                                            traffic_light_code = rating.tlc())
                except HTMLParseError:
                    pass
                self.row_text = []
    def handle_data(self, data):
        if not data.strip():
            return
        if self.read_row_text:
            if self.tables_instack() > 2:
                self.this_row_ratings = True
            self.row_text.append(data.strip())
        if self.in_syd_forecast_table:
            self.row_text.append(data.strip())
    def tables_instack(self):
        count = 0
        for tag in self.tag_stack:
            if tag == "table":
                count += 1
        return count

# Worker function, called inside a database transaction from update_data below.
def get_airdata(loader, messages, verbosity=0):
    http = httplib.HTTPConnection("airquality.environment.nsw.gov.au")
    http.request("GET", "http://airquality.environment.nsw.gov.au/aquisnetnswphp/getPage.php?reportid=25")
    resp = http.getresponse()
    clear_statistic_list("air_pollution", "syd", "rt", "regions")
    clear_statistic_list("air_pollution", "nsw", "rt", "regions")
    clear_statistic_list("air_pollution", "syd", "rt", "region_1")
    clear_statistic_list("air_pollution", "nsw", "rt", "region_1")
    parser = AirPollutionHtmlParser(messages, verbosity)
    parser.feed(resp.read())
    http.close()
    if verbosity >= 3:
        messages.append("Updated air pollution ratings from website")
    return parser.messages

# This is the interface function that is called when the loader is run.
def update_data(loader, verbosity=0):
    messages = []
    try:
        messages = call_in_transaction(get_airdata,loader, messages, verbosity)
    except HTMLParseError, e:
        raise LoaderException("Error parsing air pollution website: %s" % unicode(e))
    return messages

