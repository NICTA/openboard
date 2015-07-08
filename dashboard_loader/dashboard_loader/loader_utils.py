import decimal
import datetime
import pytz
import os
import thread

from django.conf import settings
from django.db import transaction

from dashboard_loader.models import Loader, Uploader
from widget_def.models import WidgetDefinition, Statistic, IconCode, TrafficLightScaleCode, GraphDefinition, GraphDataset, GraphCluster
from widget_data.models import WidgetData, StatisticData, StatisticListItem, GraphData

tz = pytz.timezone(settings.TIME_ZONE)

class LoaderException(Exception):
    pass

@transaction.atomic
def lock_update(app):
    try:
        loader = Loader.objects.get(app=app)
    except Loader.DoesNotExist:
        return None
    if loader.locked_by_process:
        try:
            os.getpgid(loader.locked_by_process)
            return loader
        except OSError:
            pass
    loader.lock()
    loader.save()
    return loader

def unlock_loader(loader):
    loader.locked_by_process = None
    loader.locked_by_thread = None
    loader.save()

def update_loader(loader, success=True):
    loader.last_run = datetime.datetime.now(tz)
    if success:
        loader.last_loaded = loader.last_run
    unlock_loader(loader)

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
            data.intval = value
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

def do_update(app, verbosity=0, force=False):
    _tmp = __import__(app + ".loader", globals(), locals(), ["update_data",], -1)
    update_data = _tmp.update_data
    loader = lock_update(app)
    if loader.locked_by_me():
        reason = loader.reason_to_not_run()
        if not reason or force:
            try:
                messages = update_data(loader, verbosity=verbosity)
            except LoaderException, e:
                update_loader(loader, False)
                return [ "Data update for %s failed: %s" % (app, unicode(e)) ]
            update_loader(loader)
            if verbosity > 0:
                messages.append("Data updated for %s" % app)
            return messages
        else:
            unlock_loader(loader)
            return [ reason ]
    elif verbosity > 0:
        return [ "Data update for %s is locked by another update process/thread since %s" % (app, loader.last_locked.strftime("%d/%m/%Y %H:%M:%D"))]

def get_update_format(app):
    _tmp = __import__(app + ".uploader", globals(), locals(), ["file_format",], -1)
    return _tmp.file_format

def do_upload(app, fh, actual_freq_display=None, verbosity=0):
    if isinstance(app, Uploader):
        uploader = app
        app = uploader.app
    else:
        uploader = Uploader.objects.get(app=app)
    _tmp = __import__(app + ".uploader", globals(), locals(), 
                        ["upload_file", ], -1)
    upload_file = _tmp.upload_file
    try:
        messages = upload_file(uploader, fh, actual_freq_display, verbosity)
    except LoaderException, e:
        return [ "Data upload for %s failed: %s" % (app, unicode(e)) ]
    uploader.last_uploaded = datetime.datetime.now(tz)
    uploader.save()
    if verbosity > 0:
        messages.append("Data uploaded for %s" % app)
    return messages

@transaction.atomic
def call_in_transaction(func, *args, **kwargs):
    return func(*args, **kwargs)

def get_graph(widget_url, actual_location_url, actual_frequency_url, tile_url):
    try:
        return GraphDefinition.objects.get(tile__url=tile_url, 
                tile__widget__family__url=widget_url, 
                tile__widget__actual_location__url=actual_location_url,
                tile__widget__actual_frequency__url=actual_frequency_url)
    except GraphDefinition.DoesNotExist:
        raise LoaderException("Graph for tile %s of widget %s:(%s,%s) does not exist"%(tile_url, widget_url, actual_location_url, actual_frequency_url))

def clear_graph_data(graph):
    graph.get_data().delete()

def add_graph_data(graph, dataset, value, cluster=None, horiz_value=None):
    if not isinstance(dataset, GraphDataset):
        try:
            dataset = GraphDataset.objects.get(graph=graph, url=dataset)
        except GraphDataset.DoesNotExist:
            raise LoaderException("Dataset %s for graph %s does not exist" % (str(dataset), graph.tile.url))
    value = decimal.Decimal(value).quantize(decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP)
    gd = GraphData(graph=graph, dataset=dataset,value=value)
    if graph.use_clusters():
        if not cluster:
            raise LoaderException("Must supply cluster for data for graph %s" % graph.tile.url)   
        elif not isinstance(cluster, GraphCluster):
            try:
                cluster = GraphCluster.objects.get(graph=graph, url=cluster)
            except GraphCluster.DoesNotExist:
                raise LoaderException("Cluster %s for graph %s does not exist" % (str(cluster), graph.tile.url))
        gd.cluster = cluster
    else:
        if graph.horiz_axis_type == graph.NUMERIC:
            gd.horiz_numericval = decimal.Decimal(horiz_value).quantize(decimal.Decimal("0.0001", rounding=decimal.ROUND_HALF_UP))
        elif graph.horiz_axis_type == graph.DATE:
            gd.horiz_dateval = horiz_value
        elif graph.horiz_axis_type == graph.TIME:
            gd.horiz_timeval = horiz_value
        elif graph.horiz_axis_type == graph.DATETIME:
            gd.horiz_dateval = horiz_value.date()
            gd.horiz_timeval = horiz_value.time()
    gd.save()
    return gd

def parse_date(d):
    if d is None:
        return None
    elif isinstance(d, datetime.date):
        return d
    elif isinstance(d, datetime.date):
        return d.date()
    try:
        dt = datetime.datetime.strptime(d, "%Y-%m-%d")
        return dt.date()
    except ValueError:
        raise LoaderException("Not a valid date string: %s" % repr(d))

def parse_time(t):
    if t is None:
        return None
    elif isinstance(t, datetime.time):
        return t
    elif isinstance(t, datetime.datetime):
        return t.time()
    for fmt in ("%H:%M:%S", "%H-%M-%S", "%H:%M", "%H-%M"):
        try:
            dt = datetime.datetime.strptime(t, "%H:%M:%S")
            return dt.time()
        except ValueError:
            pass
        except TypeError:
            raise LoaderException("Cannot parse t as a time: %s" % repr(t))
    raise LoaderException("Not a valid time string: %s" % repr(t))

def parse_datetime(dt):
    if dt is None:
        return None
    elif isinstance(dt, datetime.date):
        return tz.localize(dt)
    elif isinstance(dt, datetime.date):
        return tz.localize(datetime.datetime.combine(dt, datetime.time()))
    for fmt in ("%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%Y"
            ):
        try:
            dt = datetime.datetime.strptime(dt, fmt)
            return tz.localize(dt)
        except ValueError:
            pass
    try:    
        dt = datetime.datetime.strptime(dt, "%YQ%m")
        dt = dt.replace(month=(dt.month-1)*3+1)
        return tz.localize(dt)
    except ValueError:
        raise LoaderException("Not a valid date string: %s" % repr(dt))

