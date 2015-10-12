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

from widget_def.api import *
from widget_def.models import *

from django.contrib.auth.models import User, AnonymousUser
from dashboard_loader.test_util import DashboardTransactionTestCase

# Create your tests here.

class APIReferenceTests(DashboardTransactionTestCase):
    fixtures = ['test_exports/users.json']
    imports = [
        'test_exports/categories.json', 
        'test_exports/gw_Greater_Sydney.json', 
        'test_exports/views.json', 
        'test_exports/icon_race.json']

    def test_get_locations(self):
        self.assertEqual(api_get_locations(), [
                        { 'name': 'Middle Earth', 'url': 'all' },
                        { 'name': 'Gondor', 'url': 'gondor' },
                        { 'name': 'Rhovanion', 'url': 'rhovanion' },
                        { 'name': 'Arnor', 'url': 'arnor' },
        ])
    def test_get_frequencies(self):
        freqs = api_get_frequencies()
        self.assertNotIn({'name': 'Sample Data', 'url': 'sample'}, freqs)
        self.assertEqual(freqs, [
                        { 'name': 'Latest', 'url': 'rt' },
                        { 'name': 'Annual', 'url': 'year' },
                        { 'name': 'Age', 'url': 'age' },
        ])
    def test_get_themes_unauth(self):
        themes = api_get_themes(AnonymousUser())
        self.assertEqual(themes, [
                        { 'name': 'All', 'url': 'all' },
                        { 'name': 'Men', 'url': 'men' },
        ])
    def test_get_themes_auth(self):
        user = User.objects.all()[0]
        themes = api_get_themes(user)
        self.assertEqual(themes, [
                        { 'name': 'All', 'url': 'all' },
                        { 'name': 'Elves', 'url': 'elves' },
                        { 'name': 'Men', 'url': 'men' },
                        { 'name': 'Dwarves', 'url': 'dwarves' },
        ])
    def test_get_icon_libs(self):
        self.assertEqual(api_get_icon_libraries(), {
                "race": [
                        { "library": "race", "value": "elf", "alt_text": "Elves" },
                        { "library": "race", "value": "man", "alt_text": "Men" },
                        { "library": "race", "value": "dwarf", "alt_text": "Dwarves" },
                        { "library": "race", "value": "hobbit", "alt_text": "Hobbits" },
                        { "library": "race", "value": "orc", "alt_text": "Orcs" },
                        { "library": "race", "value": "maia", "alt_text": "Maia" },
                        { "library": "race", "value": "ent", "alt_text": "Ents" },
                        { "library": "race", "value": "dragon", "alt_text": "Dragons" },
                ]
        })

class APIWidgetTests(DashboardTransactionTestCase):
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

    def test_get_widgets_1(self):
        widgets_1 = self.call_get_widgets("all", "all", "rt")
        self.assertEqual(len(widgets_1), 2)
        widgets_2 = self.call_get_widgets("all", "all", "year")
        self.assertEqual(len(widgets_2), 2)
        widgets_3 = self.call_get_widgets("all", "gondor", "rt")
        self.assertEqual(len(widgets_3), 1)
        widgets_4 = self.call_get_widgets("all", "gondor", "year")
        self.assertEqual(len(widgets_4), 1)
        widgets_5 = self.call_get_widgets("men", "gondor", "rt")
        self.assertEqual(len(widgets_5), 1)
        widgets_6 = self.call_get_widgets("men", "gondor", "year")
        self.assertEqual(len(widgets_6), 1)
        widgets_7 = self.call_get_widgets("elves", "gondor", "year")
        self.assertEqual(len(widgets_7), 0)

    def call_get_widgets(self, theme_url, location_url, frequency_url):
        return api_get_widgets(
                    Theme.objects.get(url=theme_url),
                    Location.objects.get(url=location_url),
                    Frequency.objects.get(url=frequency_url))

