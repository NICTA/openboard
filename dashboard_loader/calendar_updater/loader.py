import datetime
import decimal
import random
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import clear_statistic_list, add_statistic_list_item, get_statistic, call_in_transaction

# Refresh every 2 hours
refresh_rate = 60 * 60 * 2

tz = pytz.timezone(settings.TIME_ZONE)
def update_data(loader, verbosity=0):
    messages = []
    today = datetime.date.today()
    correct_today_items = get_statistic("events", "nsw", "day", "calendar").get_data().filter(datetime_key=today)
    messages.extend(call_in_transaction(update_calendar, correct_today_items, verbosity))
    old_items = get_statistic("events", "nsw", "day", "calendar").get_data().filter(datetime_key__lt=today)
    messages.extend(call_in_transaction(clean_calendar, old_items, verbosity))
    return messages

def update_calendar(correct_today_items, verbosity=0):
    messages = []
    clear_statistic_list("events", "nsw", "day", "today")
    for correct_item in correct_today_items:
        add_statistic_list_item("events", "nsw", "day", "today", correct_item.value(), correct_item.sort_order,
                    url=correct_item.url)
        if verbosity >= 3:
            messages.append("Added %s" % correct_item.strval)
    return messages

def clean_calendar(old_items, verbosity=0):
    messages = []
    if verbosity > 1:
        messages.append("Deleting %d old events" % old_items.count())
    old_items.delete()
    return messages
   
