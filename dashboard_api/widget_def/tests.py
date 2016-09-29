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

import json

from widget_def.api import *
from widget_def.models import *

from django.contrib.auth.models import User, AnonymousUser
from dashboard_loader.test_util import DashboardTransactionTestCase, json_equal
from widget_def.view_utils import jsonize
from widget_def.models import WidgetFamily

# Create your tests here.

class APIReferenceTests(DashboardTransactionTestCase):
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
        'test_exports/icon_race.json']

    def test_top_level_views_auth(self):
        user = User.objects.all()[0]
        views = api_get_top_level_views(user)
        self.assertEqual(api_get_top_level_views(user), [
            {
                'name': u'All', 
                'label': u'tall_migration'
            }, 
            {
                'name': u'Elves', 
                'label': u'telves_migration'
            }, 
            {
                'name': u'Men', 
                'label': u'tmen_migration'
            }, 
            {
                'name': u'Dwarves', 
                'label': u'tdwarves_migration'
            }
        ])
    
    def test_top_level_views_unauth(self):
        self.assertEqual(api_get_top_level_views(AnonymousUser()), [
            {
                'name': u'All', 
                'label': u'tall_migration'
            }, 
            {
                'name': u'Men', 
                'label': u'tmen_migration'
            },
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

    def test_get_widgets_1(self):
        widgets_1 = self.get_view_by_label("tall_frt_lall_migration")
        self.assertEqual(len(widgets_1["widgets"]), 2)
        widgets_2 = self.get_view_by_label("tall_fyear_lall_migration")
        self.assertEqual(len(widgets_2["widgets"]), 2)
        widgets_3 = self.get_view_by_label("tall_frt_lgondor_migration")
        self.assertEqual(len(widgets_3["widgets"]), 1)
        widgets_4 = self.get_view_by_label("tall_fyear_lgondor_migration")
        self.assertEqual(len(widgets_4["widgets"]), 1)
        widgets_5 = self.get_view_by_label("tmen_frt_lgondor_migration")
        self.assertEqual(len(widgets_5["widgets"]), 1)
        widgets_6 = self.get_view_by_label("tmen_fyear_lgondor_migration")
        self.assertEqual(len(widgets_6["widgets"]), 1)
        widgets_7 = self.get_view_by_label("telves_fyear_lgondor_migration")
        self.assertEqual(len(widgets_7["widgets"]), 0)

    def get_view_by_label(self, lbl):
        view = WidgetView.objects.get(label=lbl)
        return api_get_view(view)

    def test_dump_widgets(self):
        widgets = [
            ('national_leadership', 'test_exports/w_national_leadership.json', ),
            ('race_rings', 'test_exports/w_race_rings.json',),
        ]
        for url, fn in widgets:
            fp = open(fn)
            file_dump = json.load(fp)
            wf = WidgetFamily.objects.get(url=url)
            raw_dump = wf.export()
            json_dump = jsonize(raw_dump)
            cooked_json = json.loads(json_dump)
            self.assertTrue(json_equal(file_dump, cooked_json, url))

