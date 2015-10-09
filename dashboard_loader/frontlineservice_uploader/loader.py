import os
import datetime
import decimal
import random
import xlrd
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import set_statistic_data, get_statistic, call_in_transaction, get_graph, add_graph_data, clear_graph_data, get_traffic_light_code
from widget_def.models import GraphDefinition

# Refresh every 5 minutes
# refresh_rate = 60 * 5

TF_QUARTER_HOUR_RANGE = 0
TF_HOUR = 1

def update_data(loader, verbosity=0):
    messages = []
    wb = get_xls_workbook(messages)
    graph_counters=get_graph("service_nsw_svc_counters", "syd", "day", "service_nsw_svc_counters_graph")
    graph_calls=get_graph("service_nsw_svc_calls", "syd", "day", "service_nsw_svc_calls_graph")
    graph_www=get_graph("service_nsw_svc_www", "syd", "day", "service_nsw_svc_www_graph")
    call_in_transaction(load_data, wb.sheets()[0], TF_QUARTER_HOUR_RANGE, 
            "customers", "wait",
            graph_counters, messages, True)
    call_in_transaction(load_data, wb.sheets()[1], TF_QUARTER_HOUR_RANGE, 
            "calls", "wait",
            graph_calls, messages, True)
    call_in_transaction(load_data, wb.sheets()[2], TF_HOUR, 
            "visits", "duration",
            graph_www, messages, True)
    wb.release_resources()
    call_in_transaction(update_widget, graph_counters, "customers", "wait",
                        "visits", "wait", TF_QUARTER_HOUR_RANGE,
                        "15:00", "10:00")
    call_in_transaction(update_widget, graph_calls, "calls", "wait",
                        "callers", "wait", TF_QUARTER_HOUR_RANGE,
                        "15:00", "10:00")
    call_in_transaction(update_widget, graph_www, "visits", "duration",
                        "visits", "duration", TF_HOUR,
                        "99:00", "99:00")
    return messages

def get_xls_workbook(messages):
    filename = os.path.join(os.path.dirname(__file__), "service_nsw_data.xlsx")
    messages.append("Reading <%s>" % filename)
    return xlrd.open_workbook(filename)

def update_widget(graph, count_dataset, duration_dataset, 
                count_statistic, duration_statistic, time_format,
                bad_duration, poor_duration):
    count_stat = get_statistic(graph.tile.widget.url, 
                        graph.tile.widget.actual_location.url, 
                        graph.tile.widget.actual_frequency.url,
                        count_statistic)
    duration_stat = get_statistic(graph.tile.widget.url, 
                        graph.tile.widget.actual_location.url,
                        graph.tile.widget.actual_frequency.url,
                        duration_statistic)
    last_count_data = graph.get_last_datum(count_dataset)
    last_duration_data = graph.get_last_datum(duration_dataset)
    # count
    if time_format == TF_QUARTER_HOUR_RANGE:
        period = 15
    else:
        period  = 60
    oldval = count_stat.get_data()
    if oldval is None:
        trend = 0
    elif oldval.value() == last_count_data.value:
        trend = 0
    elif oldval.value() < last_count_data.value:
        trend = 1
    else:
        trend = -1
    # tlc = get_traffic_light_code(count_stat, "good")
    tlc = None
    if not oldval or trend != 0:
        set_statistic_data(graph.tile.widget.url, 
                        graph.tile.widget.actual_location.url,
                        graph.tile.widget.actual_frequency.url,
                        count_statistic, last_count_data.value / decimal.Decimal(period),
                        traffic_light_code=tlc, trend=trend)
    # duration
    oldval = duration_stat.get_data()
    if oldval:
        oldval = oldval.value()

    newval_min = int(last_duration_data.value)
    newval_sec = int((last_duration_data.value - newval_min) * 60)
    newval = "%02d:%02d" % (newval_min, newval_sec)
    if oldval is None:
        trend = 0
    elif oldval < newval:
        trend = 1
    else:
        trend = -1
# if newval > bad_duration:
#    tlc = get_traffic_light_code(count_stat, "bad")
# elif newval > poor_duration:
#    tlc = get_traffic_light_code(count_stat, "poor")
# else:
#    tlc = get_traffic_light_code(count_stat, "good")
    tlc = None
    if not oldval or trend != 0:
        set_statistic_data(graph.tile.widget.url, 
                        graph.tile.widget.actual_location.url,
                        graph.tile.widget.actual_frequency.url,
                        duration_statistic, newval,
                        traffic_light_code=tlc, trend=trend)
    return

def load_data(ws, time_format, count_dataset, duration_dataset, graph, messages, fake_realtime=False):
    if not fake_realtime:
        clear_graph_data(graph)
    for row in range(ws.nrows):
        line = row + 1
        if line == 1:
            continue
        time_cell = ws.cell(row, 1).value
        count_cell = ws.cell(row, 2).value
        duration_cell = ws.cell(row,3).value
        if time_format == TF_QUARTER_HOUR_RANGE:
            (start_str,stop_str) = time_cell.split("-")
            start_str = start_str.strip()
            stop_str = stop_str.strip()
            start = datetime.datetime.strptime(start_str, "%I:%M %p").time()
            stop = datetime.datetime.strptime(stop_str, "%I:%M %p").time()
            stop_dt = datetime.datetime.combine(datetime.date.today(), stop) + datetime.timedelta(minutes=1)
            stop = stop_dt.time()
        elif time_format == TF_HOUR:
            hour = int(time_cell)
            start = datetime.time(hour=hour)
            if hour == 23:
                stop = datetime.time.max
            else:
                stop = datetime.time(hour=hour+1)
        else:
            raise LoadException("Unknown time_format")
        count = int(count_cell)
        if isinstance(duration_cell, unicode):
            d = duration_cell.strip()
            mins = d[0:2]
            secs = d[3:5]
            duration = float(secs)/60.0 + float(mins)
        else:
            duration = duration_cell * 24.0 * 60.0
        # Got start, stop, count and duration
        include_row = True
        if fake_realtime:
            now = datetime.datetime.now().time()
            if line == 2:
                if now < stop:
                    # Keep Yesterday's data
                    return
                else:
                    clear_graph_data(graph)
            if now < stop:
                include_row = False
        if include_row:
            add_graph_data(graph, count_dataset, count, horiz_value=start)
            add_graph_data(graph, duration_dataset, duration, horiz_value=start)
    return
