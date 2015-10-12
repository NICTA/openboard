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

from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser
from dashboard_loader.test_util import DashboardTransactionTestCase
from widget_data.api import *

# Create your tests here.

class WidgetDataTests(DashboardTransactionTestCase):
    fixtures = ['test_exports/users.json']
    imports = [
        'test_exports/categories.json', 
        'test_exports/gw_Greater_Sydney.json', 
        'test_exports/views.json', 
        'test_exports/icon_race.json', 
        'test_exports/tlc_leadership.json', 
        'test_exports/tlc_std-3-code.json', 
        'test_exports/w_national_leadership.json', 
        'test_exports/w_race_rings.json',
    ]
    widget_data = [
        'test_exports/d_national_leadership.json', 
        'test_exports/d_race_rings.json',
    ]
    def test_get_widget_data(self):
        data = self.call_get_widget_data("national_leadership", "all", "all", "year")
        self.assertEqual(data["actual_frequency"], "Last Year")
        self.assertEqual(len(data["statistics"]), 8)
        data = self.call_get_widget_data("national_leadership", "all", "gondor", "year")
        self.assertEqual(len(data["statistics"]), 3)
        self.assertEqual(len(data["statistics"]["recent_rulers"]), 5)
    def call_get_widget_data(self, widget_url, 
            theme_url, location_url, frequency_url):
        widget = get_declared_widget(widget_url,
                 Theme.objects.get(url=theme_url),
                    Location.objects.get(url=location_url),
                    Frequency.objects.get(url=frequency_url))
        self.assertIsNotNone(widget)
        return api_get_widget_data(widget)

