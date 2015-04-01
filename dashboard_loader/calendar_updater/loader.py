import datetime
import decimal
import random
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import add_statistic_list_item, get_statistic, call_in_transaction

# Refresh every 2 hours
refresh_rate = 60 * 60 * 2

def update_data(loader, verbosity=0):
    today = datetime.date.today()
    existing_today_items = get_statistic("events", "nsw", "day", "today").get_data()
    correct_today_items = get_statistic("events", "nsw", "day", "calendar").get_data().filter(datekey=today)
    return call_in_transaction(update_calendar,existing_today_items, correct_today_items, verbosity)

def update_calendar(existing_today_items, correct_today_items, verbosity=0):
    messages = []
    for item in existing_today_items:
        item.delete()
        if verbosity >= 3:
            messages.append("Deleted %s" % item.strval)
    for correct_item in correct_today_items:
        add_statistic_list_item("events", "nsw", "day", "today", correct_item.value(), correct_item.sort_order,
                    url=correct_item.url)
        if verbosity >= 3:
            messages.append("Added %s" % correct_item.strval)
    return messages
