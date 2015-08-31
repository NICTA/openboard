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

