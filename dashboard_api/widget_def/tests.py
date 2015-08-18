from widget_def.api import *

from django.contrib.auth.models import User, AnonymousUser
from dashboard_api.test_util import DashboardTransactionTestCase

# Create your tests here.

class APIReferenceTests(DashboardTransactionTestCase):
    fixtures = ['test_exports/reference.json', 'test_exports/users.json']
    imports =  ['test_exports/icon_race.json']

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

