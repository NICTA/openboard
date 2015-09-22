from interface import LoaderException

from widget_def.models import WidgetDefinition, Statistic, IconCode, TrafficLightScaleCode
from widget_data.models import WidgetData, StatisticData, StatisticListItem

def get_statistic(widget_url, actual_location_url, actual_frequency_url, statistic_url):
    try:
        return Statistic.objects.get(url=statistic_url, 
                tile__widget__family__url=widget_url, 
                tile__widget__actual_location__url=actual_location_url,
                tile__widget__actual_frequency__url=actual_frequency_url)
    except Statistic.DoesNotExist:
        raise LoaderException("Statistic %s for Widget %s(%s,%s) does not exist" % (statistic_url, widget_url, actual_location_url, actual_frequency_url))

def clear_statistic_data(widget_url, actual_location_url, actual_frequency_url, 
                statistic_url):
    stat = get_statistic(widget_url, actual_location_url, actual_frequency_url,
                                    statistic_url)
    if stat.is_data_list():
        raise LoaderException("Statistic %s is a list statistic" % statistic_url)
    data = stat.get_data()
    if data:
        data.delete()
 
def set_statistic_data(widget_url, 
                    actual_location_url, actual_frequency_url, 
                    statistic_url, 
                    value, 
                    traffic_light_code=None, icon_code=None, 
                    trend=None, label=None):
    stat = get_statistic(widget_url, actual_location_url, actual_frequency_url,
                                    statistic_url)
    if stat.is_data_list():
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
            data.intval = value + 0.5
        else:
            data.decval = value
    else:
        data.strval = value
    try:
        data.save()
    except Exception, e:
        raise LoaderException(str(e))

def clear_statistic_list(widget_url, actual_location_url, actual_frequency_url, 
                statistic_url):
    stat = get_statistic(widget_url, actual_location_url, actual_frequency_url, statistic_url)
    stat.statisticlistitem_set.all().delete()
    
def add_statistic_list_item(widget_url, actual_location_url, actual_frequency_url, 
                statistic_url, 
                value, sort_order, 
                datetimekey=None, datetimekey_level=None, datekey=None, label=None, 
                traffic_light_code=None, icon_code=None, trend=None, url=None):
    stat = get_statistic(widget_url, actual_location_url, actual_frequency_url, statistic_url)
    if not stat.is_data_list():
        raise LoaderException("Not a list statistic %s" % statistic_url)
    if stat.is_kvlist() and not label:
        raise LoaderException("Must provide a label for list items for statistic %s" % statistic_url)
    elif not stat.is_display_list() and not stat.name_as_label and not label:
        raise LoaderException("Must provide a label for list items for statistic %s" % statistic_url)
    elif not stat.is_display_list() and stat.name_as_label and label:
        raise LoaderException("Cannot provide a label for list items for statistic %s" % statistic_url)
    elif stat.is_display_list() and not stat.is_kvlist() and label:
        raise LoaderException("Cannot provide a label for list items for statistic %s" % statistic_url)
    if stat.use_datekey() and not datekey:
        raise LoaderException("Must provide a datekey for list items for statistic %s" % statistic_url)
    elif datekey and not stat.use_datekey():
        raise LoaderException("Cannot provide a datekey for list items for statistic %s" % statistic_url)
    if stat.use_datetimekey() and not datetimekey:
        raise LoaderException("Must provide a datetimekey for list items for statistic %s" % statistic_url)
    elif datetimekey and not stat.use_datetimekey():
        raise LoaderException("Cannot provide a datetimekey for list items for statistic %s" % statistic_url)
    if stat.use_datetimekey_level() and not datetimekey_level:
        raise LoaderException("Must provide a datetimekey level for list items for statistic %s" % statistic_url)
    elif datetimekey_level and not stat.use_datetimekey_level():
        raise LoaderException("Cannot provide a datetimekey level for list items for statistic %s" % statistic_url)
    if stat.trend and trend is None:
        raise LoaderException("Must provide a trend for statistic %s" % statistic_url)
    if not stat.hyperlinkable and url is not None:
        raise LoaderException("Cannnot provide a url for statistic %s (not hyperlinkable)" % statistic_url)
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
    if datekey:
        datetimekey = datekey
    if datetimekey_level:
        if not isinstance(datetimekey_level, int):
            for lc in StatisticListItem.level_choices:
                if lc[1] == datetimekey_level:
                    datetimekey_level = lc[0]
                    break
    item = StatisticListItem(statistic=stat, keyval=label, trend=trend,
            sort_order=sort_order, datetime_key=datetimekey, datetime_keylevel=datetimekey_level,
            traffic_light_code=tlc, icon_code=ic, url=url)
    if stat.is_numeric():
        if stat.num_precision == 0:
            item.intval = value
        else:
            item.decval = value
    else:
        item.strval = value
    item.save()

def set_actual_frequency_display_text(widget_url, actual_location_url,
                    actual_frequency_url, display_text):
    try:
        wdef = WidgetDefinition.objects.get(family__url=widget_url,
                                actual_location__url=actual_location_url,
                                actual_frequency__url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        raise LoaderException("Widget %s(%s,%s) does not exist" % (widget_url, actual_location_url, actual_frequency_url))
    wdata = wdef.widget_data()
    if not wdata:
        wdata = WidgetData(widget=wdef)
    wdata.actual_frequency_text = display_text
    wdata.save()
             
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

