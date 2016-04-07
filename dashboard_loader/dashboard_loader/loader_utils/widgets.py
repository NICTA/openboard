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

import decimal
from interface import LoaderException

from widget_def.models import WidgetDefinition, Statistic, IconCode, TrafficLightScaleCode
from widget_data.models import WidgetData, StatisticData, StatisticListItem

def get_statistic(widget_url_or_stat, label=None, statistic_url=None):
    """If called with a Statistic object as the first argument, simply return the first
argument.  Otherwise interpret the arguments as defined below, look up the indicated 
Statistic object and return it.

widget_url_or_stat: The url of the widget to which the requested Statistic belong.

label: The label for the widget definition to which the requested statistic belongs.

statistic_url: The url of the requested statistic.

Raises LoaderException if the requested Statistic does not exist.
"""
    if isinstance(widget_url_or_stat, Statistic):
        return widget_url_or_stat
    try:
        return Statistic.objects.get(url=statistic_url, 
                tile__widget__family__url=widget_url_or_stat, 
                label=label)
    except Statistic.DoesNotExist:
        raise LoaderException("Statistic %s for Widget %s(%s) does not exist" % (statistic_url, widget_url_or_stat, label))

def clear_statistic_data(widget_url_or_stat, 
                actual_location_url=None, actual_frequency_url=None, 
                statistic_url=None):
    """Clear data for the requested statistic (which must be scalar: non-list)

Interprets arguments as for the get_statistic function.

Raises LoaderException if the requested Statistic does not exist or is a list.
"""
    stat = get_statistic(widget_url_or_stat, actual_location_url, actual_frequency_url,
                                    statistic_url)
    if stat.is_data_list():
        raise LoaderException("Statistic %s is a list statistic" % statistic_url)
    data = stat.get_data()
    if data:
        data.delete()
 
def set_statistic_data(widget_url, 
                    label,
                    statistic_url, 
                    value, 
                    traffic_light_code=None, icon_code=None, 
                    trend=None, label=None):
    """Equivalent to get_stat_data, but with a get_statistic lookup of the statistic"""
    stat = get_statistic(widget_url, label, statistic_url)
    set_stat_data(stat, value, traffic_light_code, icon_code, trend, label)

def set_stat_data(stat,
                    value, 
                    traffic_light_code=None, icon_code=None, 
                    trend=None, label=None):
    """Set the data for a scalar statistic.

stat: A non-list Statistic object
value: The value to set the data to. Must be of the appropriate type for the statistic.
traffic_light_code: The TrafficLightScaleCode object (or value string) to set the traffic light value to
icon_code: The IconCode object (or value string, or numeric id) to set the icon value to
trend: The trend indicator value (+1: up, -1: down, 0: steady)
label: The dynamic label for the statistic.

If any arguments are required according to the statistic meta-data and not supplied (or vice versa), a
LoaderException is raised.
"""
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
    apply_traffic_light_automation(stat)

def clear_statistic_list(widget_url_or_stat, 
                label=None,
                statistic_url=None):
    """Clear data for the requested statistic (which must be a list)

Interprets arguments as for the get_statistic function.

Raises LoaderException if the requested Statistic does not exist or is not a list.
"""
    stat = get_statistic(widget_url_or_stat, label, statistic_url)
    stat.statisticlistitem_set.all().delete()
    
def add_statistic_list_item(widget_url, label,
                statistic_url, 
                value, sort_order, 
                datetimekey=None, datetimekey_level=None, datekey=None, label=None, 
                traffic_light_code=None, icon_code=None, trend=None, url=None):
    """Equivalent to add_stat_list_item, but with a get_statistic lookup of the statistic"""
    stat = get_statistic(widget_url, label, statistic_url)
    add_stat_list_item(stat, value, sort_order,
                datetimekey, datetimekey_level, datekey, label,
                traffic_light_code, icon_code, trend, url)

def add_stat_list_item(stat,
                value, sort_order, 
                datetimekey=None, datetimekey_level=None, datekey=None, label=None, 
                traffic_light_code=None, icon_code=None, trend=None, url=None):
    """Add an item for a list statistic.

stat: A list Statistic object
value: The value for the new item. Must be of the appropriate type for the statistic.
datetimekey: The datetime key for the item
datetimekey_level: The datetime "level" at which the datetimekey is to be interpreted.
        (Must be one of the numeric values defined in widget_data.models.stat_list.StatisticListItem)
datekey: The date key for the item
traffic_light_code: The TrafficLightScaleCode object (or value string) for the new item
icon_code: The IconCode object (or value string, or numeric id) for the new item
trend: The trend indicator value (+1: up, -1: down, 0: steady) for the new item
label: The label (string key) for the item.
url: The hyperlink (url) for the item.

If any arguments are required according to the statistic meta-data and not supplied (or vice versa), a
LoaderException is raised.
"""
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
    apply_traffic_light_automation(stat)

def set_actual_frequency_display_text(widget_url, label, display_text):
    """Set the actual frequency display text of the indicated widget"""
    try:
        wdef = WidgetDefinition.objects.get(family__url=widget_url,
                                label=label)
    except WidgetDefinition.DoesNotExist:
        raise LoaderException("Widget %s(%s) does not exist" % (widget_url, label))
    set_widget_actual_frequency_display_text(wdef, display_text)

def set_widget_actual_frequency_display_text(widget, display_text):
    wdata = widget.widget_data()
    if not wdata:
        wdata = WidgetData(widget=widget)
    wdata.actual_frequency_text = display_text
    wdata.save()

def get_icon(library, lookup):
    """Lookup icon code by icon library name and icon name or sort_order"""
    try: 
        if isinstance(lookup, int):
            return IconCode.objects.get(scale__name=library, sort_order=lookup)
        else:
            return IconCode.objects.get(scale__name=library, value=lookup)
    except IconCode.DoesNotExist:
        raise LoaderException("Icon code %s:%s does not exist" % (library, lookup))

def get_traffic_light_code(stat, value):
    """Lookup traffic light code for a statistic by value"""
    if not stat.traffic_light_scale:
        raise LoaderException("Statistic %s does not have a traffic light scale" % stat.url)
    try:
        return stat.traffic_light_scale.trafficlightscalecode_set.get(value=value)
    except TrafficLightScaleCode.DoesNotExist:
        raise LoaderException("Traffic light code %s not found in scale %s for statistic %s" % (value,stat.traffic_light_scale.name, stat.url))

def apply_traffic_light_automation(stat):
    for auto in stat.trafficlightautomation_set.all():
        for autostat in auto.statistic_set.all():
            apply_traffic_light_automation(autostat)
    auto = stat.traffic_light_automation
    if not auto:
        return
    metric_data = stat.get_data()
    if not metric_data:
        return
    if not stat.is_data_list():
        metric_data = [ metric_data ]
    if auto.target_statistic:
        target_value = decimal.Decimal(auto.target_statistic.get_data().value())
    elif auto.target_value:
        target_value = auto.target_value
    else:
        target_value = None
    for datum in metric_data:
        metric_value = datum.value()
        if stat.is_numeric():
            metric_value = decimal.Decimal(metric_value)
        datum.traffic_light_code = auto.strategy.traffic_light_for(metric_value, target_value)
        datum.save()
    return

