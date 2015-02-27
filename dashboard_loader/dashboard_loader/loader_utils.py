import datetime
import pytz
import os

from django.conf import settings
from django.db import transaction

from dashboard_loader.models import Loader
from widget_def.models import Statistic, IconCode, TrafficLightScaleCode
from widget_data.models import StatisticData, StatisticListItem

class LoaderException(Exception):
    pass

@transaction.atomic
def lock_update(app):
    try:
        loader = Loader.objects.get(app=app)
    except Loader.DoesNotExist:
        return None
    if loader.locked_by:
        try:
            os.getpgid(loader.locked_by)
            return loader
        except OSError:
            pass
    loader.locked_by = os.getpid()
    loader.save()
    return loader

def update_loader(loader, success=True):
    tz = pytz.timezone(settings.TIME_ZONE)
    loader.last_run = datetime.datetime.now(tz)
    if success:
        loader.last_loaded = loader.last_run
    loader.locked_by = None
    loader.save()

def get_statistic(widget_url, widget_actual_frequency_url, statistic_url):
    try:
        return Statistic.objects.get(url=statistic_url, tile__widget__url=widget_url, tile__widget__actual_frequency_url=widget_actual_frequency_url)
    except Statistic.DoesNotExist:
        raise LoaderException("Statistic %s for Widget %s.%s does not exist" % (statistic_url, widget_url, widget_actual_frequency_url))

def clear_statistic_data(widget_url, widget_actual_frequency_url, 
                statistic_url):
    stat = get_statistic(widget_url, widget_actual_frequency_url,
                                    statistic_url)
    if stat.is_list():
        raise LoaderException("Statistic %s is a list statistic" % statistic_url)
    data = stat.get_data()
    if data:
        data.delete()
 
def set_statistic_data(widget_url, widget_actual_frequency_url, statistic_url, 
                    value, 
                    traffic_light_code=None, icon_code=None, 
                    trend=None, label=None):
    stat = get_statistic(widget_url, widget_actual_frequency_url,
                                    statistic_url)
    if stat.is_list():
        raise LoaderException("Statistic %s is a list statistic" % statistic_url)
    data = stat.get_data()
    if not data:
        data = StatisticData(statistic=stat)
    if not stat.name_as_label and not label:
        raise LoaderException("Must provide a label for statistic %s" % statistic_url)
    else:
        data.label = label
    if stat.trend and trend is None:
        raise LoaderException("Must provide a trend for statistic %s" % statistic_url)
    else:
        data.trend = trend
    if stat.traffic_light_scale and not traffic_light_code:
        raise LoaderException("Must provide a traffic light code for statistic %s" % statistic_url)
    if stat.traffic_light_scale and isinstance(traffic_light_code, TrafficLightScaleCode):
        tlc = traffic_light_code
    elif stat.traffic_light_scale:
        tlc = get_traffic_light_code(stat, traffic_light_code)
    else:
        tlc = None
    data.traffic_light_code = tlc
    if stat.icon_library and not icon_code:
        raise LoaderException("Must provide a icon code for statistic %s" % statistic_url)
    if stat.icon_library and isinstance(icon_code, IconCode):
        ic = icon_code
    elif stat.icon_library:
        ic = get_icon(stat.icon_library.name, icon_code)
    else:
        ic = None
    data.icon_code = ic
    if stat.is_numeric():
        if stat.num_precision == 0:
            data.intval = value
        else:
            data.decval = value
    else:
        data.strval = value
    try:
        data.save()
    except Exception, e:
        raise LoaderException(str(e))

def clear_statistic_list(widget_url, widget_actual_frequency_url, statistic_url):
    stat = get_statistic(widget_url, widget_actual_frequency_url, statistic_url)
    stat.statisticlistitem_set.all().delete()
    
def add_statistic_list_item(widget_url, widget_actual_frequency_url, statistic_url, value, sort_order, 
                label=None, traffic_light_code=None, icon_code=None, trend=None, url=None):
    stat = get_statistic(widget_url, widget_actual_frequency_url, statistic_url)
    if not stat.is_list():
        raise LoaderException("Not a list statistic %s" % statistic_url)
    if stat.is_kvlist() and not label:
        raise LoaderException("Must provide a label for list items for statistic %s" % statistic_url)
    elif not stat.is_kvlist() and label:
        raise LoaderException("Cannot provide a label for list items for statistic %s" % statistic_url)
    if stat.trend and trend is None:
        raise LoaderException("Must provide a trend for statistic %s" % statistic_url)
    if stat.hyperlinkable:
        stat.url = url 
    if stat.traffic_light_scale and not traffic_light_code:
        raise LoaderException("Must provide a traffic light code for statistic %s" % statistic_url)
    if stat.icon_library and not icon_code:
        raise LoaderException("Must provide a icon code for statistic %s" % statistic_url)
    if stat.traffic_light_scale and isinstance(traffic_light_code, TrafficLightScaleCode):
        tlc = traffic_light_code
    elif stat.traffic_light_scale:
        tlc = get_traffic_light_code(stat, traffic_light_code)
    else:
        tlc = None
    if stat.icon_library and isinstance(icon_code, IconCode):
        ic = icon_code
    elif stat.icon_library:
        ic = get_icon(stat.icon_library.name, icon_code)
    else:
        ic = None
    item = StatisticListItem(statistic=stat, keyval=label, trend=trend,
            sort_order=sort_order, 
            traffic_light_code=tlc, icon_code=ic)
    if stat.is_numeric():
        if stat.num_precision == 0:
            item.intval = value
        else:
            item.decval = value
    else:
        item.strval = value
    item.save()
             
def get_icon(library, lookup):
    try: 
        if isinstance(lookup, int):
            return IconCode.objects.get(scale__name=library, sort_order=lookup)
        else:
            return IconCode.objects.get(scale__name=library, value=lookup)
    except IconCode.DoesNotExist:
        raise LoaderException("Icon code %s:%s does not exist" % (library, lookup))

def get_traffic_light_code(stat, value):
    if not stat.traffic_light_scale:
        raise LoaderException("Statistic %s does not have a traffic light scale" % stat.url)
    try:
        return stat.traffic_light_scale.trafficlightscalecode_set.get(value=value)
    except TrafficLightScaleCode.DoesNotExist:
        raise LoaderException("Traffic light code %s not found in scale %s for statistic %s" % (value,stat.traffic_light_scale.name, stat.url))

def do_update(app, verbosity=0):
    _tmp = __import__(app + ".loader", globals(), locals(), ["update_data",], -1)
    update_data = _tmp.update_data
    loader = lock_update(app)
    if loader.locked_by_me():
        try:
            messages = update_data(loader, verbosity=verbosity)
        except LoaderException, e:
            update_loader(loader, False)
            return [ "Data update for %s failed: %s" % (app, unicode(e)) ]
        update_loader(loader)
        if verbosity > 0:
            messages.append("Data updated for %s" % app)
        return messages
    elif verbosity > 0:
        return [ "Data update for %s is locked by another update process" % app]

@transaction.atomic
def call_in_transaction(func, *args, **kwargs):
    return func(*args, **kwargs)

