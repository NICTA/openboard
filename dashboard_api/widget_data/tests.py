#   Copyright 2015,2016 NICTA
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
from widget_def.models import WidgetView

# Create your tests here.

class WidgetDataTests(DashboardTransactionTestCase):
    fixtures = ['test_exports/users.json']
    imports = [
        'test_exports/categories.json', 
        'test_exports/gw_Greater_Sydney.json', 
        'test_exports/view_all.json', 
        'test_exports/view_elves.json', 
        'test_exports/view_men.json', 
        'test_exports/view_dwarves.json', 
        'test_exports/param_location.json',
        'test_exports/param_location_theme.json',
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
        data = self.call_get_widget_data("national_leadership", "tall_fyear_lall_migration")
        self.assertEqual(data["actual_frequency"], "Last Year")
        self.assertEqual(len(data["data"]), 8)
        data = self.call_get_widget_data("national_leadership", "tall_fyear_lgondor_migration")
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(len(data["data"]["recent_rulers"]), 5)
    def call_get_widget_data(self, widget_url, view_label): 
        view = WidgetView.objects.get(label=view_label)
        widget = get_declared_widget(widget_url, view)
        self.assertIsNotNone(widget)
        return api_get_widget_data(widget)

