#   Copyright 2016 NICTA
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


import datetime
import csv
import math
from scipy import stats
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from widget_def.models import Parametisation, ParametisationValue
from coag_uploader.models import *
from django.template import Template, Context

def column_labels(mini, maxi):
    labels=[]
    alphabet = [ chr(i) for i in range(ord('A'), ord('A') + 26) ]
    alphabetp = [''] + alphabet
    ri = 0
    for c0 in alphabetp:
        for c1 in alphabet:
            ri += 1
            col = c0 + c1
            if ri >= mini and ri <= maxi:
                labels.append(col)
            if ri > maxi:
                return labels

def find_state_cols(sheet, row):
    state_cols = {}
    try:
        for col in column_labels(sheet.min_column, sheet.max_column):
           val = sheet["%s%d" % (col, row)].value
           if val in state_map:
                state_cols[state_map[val]] = col
    except IndexError:
           pass
    return state_cols

def zero_all_rows(rows):
    for k in rows.keys():
        rows[k] = 0

def all_rows_found(rows):
    for k in rows.keys():
        if not rows[k]:
            return False
    return True

def load_state_grid(wb, sheet_name, data_category, dataset, abort_on, model, first_cell_rows, intermediate_cell_rows, verbosity=0, transforms={}, fld_defaults={}, use_dates=True, multi_year=False):
    messages = []
    if verbosity > 2:
        messages.append("Loading %s Data: %s" % (data_category, dataset))
    sheet = wb[sheet_name]
    state_cols = {}
    row = 1
    while not state_cols:
        state_cols = find_state_cols(sheet, row)
        row += 1
        if not state_cols and row > sheet.max_row:
            raise LoaderException("No State Columns found in worksheet '%s'" % sheet_name)
    year = 0
    isfy = False
    myr = 1
    rows = {}
    for fld in first_cell_rows.keys():
        rows[fld] = 0
    for fld in intermediate_cell_rows.keys():
        rows[fld] = 0
    while True:
        try:
            first_cell=sheet["A%d" % row].value
        except IndexError:
            break
        if first_cell:
            if isinstance(first_cell, unicode):
                first_cell = first_cell.strip()
            if first_cell == abort_on:
                break
            first_cell_matched = False
            for fld, fcr in first_cell_rows.items():
                if first_cell == fcr:
                    first_cell_matched=True
                    rows[fld] = row
                    break
            if not first_cell_matched and use_dates:
                try:
                    if multi_year:
                        (_year, _myr) = parse_multiyear(first_cell)
                    else:
                        (_year, _isfy) = parse_year(first_cell)
                    new_year = False
                    if _year != year:
                         year = _year
                         new_year = True
                    if _myr != myr:
                         myr = _myr
                         new_year = True
                    if _isfy != isfy:
                         isfy = _isfy
                         new_year = True
                    if new_year:
                        zero_all_rows(rows)
                except:
                    pass
        if year or not use_dates:
            for col in column_labels(2, sheet.max_column):
                if col in state_cols.values():
                    break
                cval = sheet["%s%d" % (col, row)].value
                if isinstance(cval, unicode):
                    cval = cval.strip()
                for fld, icr in intermediate_cell_rows.items():
                    if cval == icr:
                        rows[fld]=row
                        break
                if all_rows_found(rows):
                    for state, scol in state_cols.items():
                        if use_dates:
                            defaults = { "financial_year": isfy, "multi_year": myr }
                        else:
                            defaults = {}
                        for fld, frow in rows.items():
                            rawval = sheet["%s%d" % (scol, frow)].value
                            if fld in transforms:
                                defaults[fld] = transforms[fld](rawval)
                            else:
                                defaults[fld] = rawval
                        for def_fld, def_val in fld_defaults.items():
                            defaults[def_fld] = def_val
                        kwargs = { "state": state, "defaults": defaults }
                        if use_dates:
                            kwargs["year"] = year
                        obj, created = model.objects.update_or_create(**kwargs)
                    zero_all_rows(rows)
        row += 1
    return messages

def flt_year_equal(y1,y2):
    return abs(y1-y2) < 1e-6

def current_float_year():
    today=datetime.date.today()
    flt_year = float(today.year)
    if today.month >= 7:
        flt_year += 0.5
    return flt_year

def find_trend(metrics, reference_year, target_year):
    reference = None
    datum = None
    years = []
    data = []
    for metric in metrics:
        years.append(metric[0])
        data.append(metric[1])
        if flt_year_equal(metric[0], reference_year):
            reference = metric[1]
        if flt_year_equal(metric[0], target_year):
            datum = metric[1]
    if reference is None:
        return None
    if datum is None:
        slope, intercept, r_val, p_val, std_err = stats.linregress(years,data)
        datum = slope * target_year + intercept
        projected = True
    else:
        projected = False
    return {
            "datum": datum, 
            "reference": reference, 
            "benchmark": (datum-reference)/reference,
            "projected": projected
    }

TARGET_RELATIVE_CHANGE = 1
TARGET_ABSOLUTE_CHANGE = 2
TARGET_ABSOLUTE_VALUE  = 3

def benchmark_met(target, trend,
                desire_overtarget, target_type):
    if target_type == TARGET_RELATIVE_CHANGE:
        return (desire_overtarget and trend["benchmark"] >= target) or (not desire_overtarget and trend["benchmark"] <= target)
    elif target_type == TARGET_ABSOLUTE_CHANGE:
        return (desire_overtarget and trend["datum"]-trend["reference"] >= target) or (not desire_overtarget and trend["datum"]-trend["reference"] <= target)
    else:
        return (desire_overtarget and trend["datum"] >= target) or (not desire_overtarget and trend["datum"] <= target)

def calculate_benchmark(reference_year, target_year, 
                    target, desire_overtarget, 
                    model, benchmark_field, 
                    widget_url, widget_label, 
                    verbosity, target_type=TARGET_RELATIVE_CHANGE):
    messages = []
    metrics = [ (obj.float_year(), float(getattr(obj,benchmark_field))) for obj in model.objects.filter(state=AUS).order_by("year", "financial_year") ]
    trend = find_trend(metrics, reference_year, target_year)
    if trend:
        if benchmark_met(target, trend, desire_overtarget, target_type):
            if trend["projected"]:
                if target_year >= current_float_year():
                    tlc = "likely_to_have_been_met"
                else:
                    tlc = "on_track"
            else:
                tlc = "achieved"
        else:
            if trend["projected"]:
                if target_year >= current_float_year():
                    tlc = "unlikely_to_have_been_met"
                else:
                    tlc = "not_on_track"
            else:
                tlc = "not_met"
        if trend["projected"]:
            outcome_type = "projection"     
        else:
            outcome_type = "complete"
        if target_type == TARGET_RELATIVE_CHANGE:
            benchmark = trend["benchmark"]*100.0
        elif target_type == TARGET_ABSOLUTE_CHANGE:
            benchmark = trend["datum"] - datum["reference"]
        else:
            benchmark = trend["datum"]
        datum = trend["datum"]
        reference = trend["reference"]
    else:
        benchmark = 0.0
        reference = 0.0
        datum = 0.0
        outcome_type = "N/A"
        tlc = "new_revised_benchmark"
    set_statistic_data(widget_url, widget_label, "outcome", 
                    abs(benchmark), traffic_light_code=tlc, 
                    trend=cmp(datum, reference))
    set_statistic_data(widget_url, widget_label, "outcome_type", 
                    outcome_type)
    set_statistic_data(widget_url, widget_label, "benchmark", 
                    abs(target*100.0), trend=cmp(target, 0.0))
    set_statistic_data(widget_url, widget_label, "benchmark_year", 
                    display_float_year(target_year))
    clear_statistic_list(widget_url, widget_label, "data")
    add_statistic_list_item(widget_url, widget_label, "data",
                            reference, 10,
                            label=display_float_year(reference_year))
    last_metric = metrics[-1]
    add_statistic_list_item(widget_url, widget_label, "data",
                            last_metric[1], 20,
                            label=display_float_year(last_metric[0]))
    return messages

def calculate_indicator(desire_increase, 
                    model, indicator_field, 
                    widget_url, widget_label, 
                    verbosity):
    messages = []
    metrics = [ (obj.float_year(), float(getattr(obj,indicator_field))) for obj in model.objects.filter(state=AUS).order_by("year", "financial_year") ]
    if desire_increase:
        indicator_trend = 1
    else:
        indicator_trend = -1
    if len(metrics) == 0:
        # New indicator
        trend = 0
        tlc = "mixed_results_or_new_indicator"
        outcome_years = "N/A"
        old = None
        new = None
    else:
        if len(metrics) == 1:
            old = metrics[0]
            new = None
            trend = 0
            outcome_years = "%s" % display_float_year(old[0])
        else:
            old = metrics[0]
            new = metrics[-1]
            trend = cmp(new[1],old[1])
            outcome_years = "%s - %s" % (display_float_year(old[0]), display_float_year(new[0]))
        if trend == 0:
            tlc = "no_improvement"
        elif (trend > 0 and desire_increase) or (trend < 0 and not desire_increase):
            tlc = "improving"
        else:
            tlc = "negative_change"
    set_statistic_data(widget_url, widget_label, "outcome", 
                    "", traffic_light_code=tlc, 
                    trend=trend)
    set_statistic_data(widget_url, widget_label, "outcome_years", 
                    outcome_years)
    set_statistic_data(widget_url, widget_label, "indicator", 
                    "", trend=indicator_trend)
    clear_statistic_list(widget_url, widget_label, "data")
    if old:
        add_statistic_list_item(widget_url, widget_label, "data",
                    old[1], 10, label=display_float_year(old[0]))
    if new:
        add_statistic_list_item(widget_url, widget_label, "data",
                    new[1], 20, label=display_float_year(new[0]))
    return messages

benchmark_statuses = {
    "achieved": {
        "short": "Achieved",
        "long": "The final assessment date for the benchmark has passed. The benchmark was met.",
        "tlc": "achieved",
        "icon": "yes",
    },
    "on_track": {
        "short": "On track",
        "long": "The final assessment date for this benchmark is in the future. On the basis of results so far, the benchmark is on track to be met.",
        "tlc": "on_track",
        "icon": "yes",
    },
    "likely_to_have_been_met": {
        "short": "Likely to have been met",
        "long": "The due date for the benchmark assessment has passed, but we do not yet have data to assess results at that date. On the basis of the available data, the benchmark is likely to have been met.",
        "tlc": "likely_to_have_been_met",
        "icon": "yes",
    },
    "unlikely_to_have_been_met": {
        "short": "Unlikely to have been met",
        "long": "The due date for the benchmark assessment has passed, but we do not yet have data to assess results at that date. On the basis of the available data, the benchmark is unlikely to have been met.",
        "tlc": "unlikely_to_have_been_met",
        "icon": "warning",
    },
    "not_on_track": {
        "short": "Not on track",
        "long": "The final assessment date for this benchmark is in the future. On the basis of results so far, the benchmark is not on track to be met.",
        "tlc": "on_track",
        "icon": "warning",
    },
    "not_met": {
        "short": "Not met",
        "long": "The final assessment date for the benchmark is has passed. The benchmark was not met.",
        "tlc": "not_met",
        "icon": "no",
    },
    "new_benchmark": {
        "short": "New benchmark",
        "long": "There is no time series data available for this benchmark yet, so it is not possible to assess progress at this point.",
        "tlc": "new_benchmark",
        "icon": "unknown",
    },
    "revised_benchmark": {
        "short": "Revised benchmark",
        "long": "An agreement has been reached to replace a previous benchmark.",
        "tlc": "revised_benchmark",
        "icon": "unknown",
    },
    "mixed_results": {
        "short": "Mixed Results",
        "long": "This benchmark includes a suite of results, which have shown a variety of positive, negative and/or no change. It is not possible to form an overall traffic light assessment.",
        "tlc": "mixed_results",
        "icon": "unknown",
    },
}
indicator_statuses = {
    "improving": {
        "short": "Improving",
        "long": "There has been a noticable improvement on this measure.",
        "tlc": "improving",
        "icon": "yes",
    },
    "no_improvement": {
        "short": "No Improvement",
        "long": "There has been no noticable change across this measure.",
        "tlc": "no_improvement",
        "icon": "warning",
    },
    "negative_change": {
        "short": "Negative change",
        "long": "There has been a noticable worsening on this measure.",
        "tlc": "negative_change",
        "icon": "no",
    },
    "mixed_results": {
        "short": "Mixed results",
        "long": "This indicator includes a suite of results, which have shown a variety of positive, negative and/or no change. It is not possible to form an overall traffic light assessment.",
        "tlc": "mixed_results",
        "icon": "unknown",
    },
    "new_indicator": {
        "short": "New indicator",
        "long": "There is no time series data available for this indicator yet, so it is not possible to assess progress at this point.",
        "tlc": "new_indicator",
        "icon": "unknown",
    },
    "no_data": {
        "short": "No data",
        "long": "There is no data available for this indicator, so it is not possible to assess progress.",
        "tlc": "no_data",
        "icon": "unknown",
    },
}

def load_benchmark_description(wb, sheetname, indicator=False, additional_lookups={}):
    key_lookup = {
        "benchmark": "measure",
        "indicator": "measure",
        "benchmark/indicator": "measure",
        "benchmark/ indicator": "measure",
        "short title": "short_title",
        "status": "status",
        "updated": "updated",
        "desc body": "body",
        "description body": "body",
        "body": "body",
        "description": "body",
        "other benchmarks": "other",
        "other": "other",
        "other_indicators": "other",
        "influences": "influences",
        "notes": "notes",
        "nsw": "nsw",
        "vic": "vic",
        "qld": "qld",
        "wa": "wa",
        "sa": "sa",
        "tas": "tas",
        "act": "act",
        "nt": "nt",
        "australia": "australia",
        "aust": "australia",
    }
    sheet = wb[sheetname]
    desc = {}
    append_to = None
    row = 1
    if indicator:
        statuses = indicator_statuses
    else:
        statuses = benchmark_statuses
    key_lookup.update(additional_lookups)
    while True:
        try:
            rawkey = sheet["A%d" % row].value
        except IndexError:
            break
        if rawkey:
            key = key_lookup[rawkey.lower()]
        value = sheet["B%d" % row].value
        if key == "status":
            status = None
            for sv in statuses.values():
                if value.lower() in (sv["tlc"], sv["short"].lower()):
                    status = sv
                    break
            if not status:
                raise LoaderException("Unrecognised benchmark status: %s" % value)
            desc["status"] = status
        elif key == "updated":
            desc["updated"] = value
        elif key == "measure":
            desc["measure"] = value
        elif key == "short_title":
            desc["short_title"] = value
        elif key == "body":
            desc["body"] = []
            append_to = desc["body"]
            key = None
        elif key == "influences":
            desc["influences"] = []
            append_to = desc["influences"]
            key = None
        elif key == "notes":
            desc["notes"] = []
            append_to = desc["notes"]
            key = None
        elif key == "other":
            desc["other"] = []
            append_to = desc["other"]
            key = None
        elif key in additional_lookups.keys():
            desc[key_lookup[key]] = []
            append_to = desc[key_lookup[key]]
            key = None
        elif key in ("nsw", "vic", "qld", "wa", "sa", "tas", 
                        "act", "nt", "australia"):
            desc[key] = []
            append_to = desc[key]
            key = None
        if not key:
            append_to.append(value)
        row += 1
    return desc

def populate_raw_data(widget_url, label, rds_url,
                    model, field_map, pval=None):
    messages = []
    rds = get_rawdataset(widget_url, label, rds_url)
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    for obj in model.objects.all().order_by("state", "year", "financial_year"):
        kwargs = {
            "jurisdiction": obj.state_display(),
            "year": obj.year_display()
        }
        for model_field, rds_field in field_map.items():
            kwargs[rds_field] = unicode(getattr(obj, model_field))
        if pval:
            kwargs["pval"] = pval
        add_rawdatarecord(rds, sort_order, **kwargs)
        sort_order += 1
    return messages

def populate_crosstab_raw_data(widget_url, label, rds_url,
                    model, field_map, field_map_states=None, pval=None):
    messages = []
    if field_map_states is None:
        field_map_states = field_map
    rds = get_rawdataset(widget_url, label, rds_url)
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    kwargs = {}
    kwargs["year"] = None
    if pval:
        kwargs["pval"] = pval
    for obj in model.objects.all().order_by("year", "financial_year", "state"):
        if obj.year_display() != kwargs["year"]:
            add_rawdatarecord(rds, sort_order, **kwargs)
            sort_order += 1
            kwargs = {}
            kwargs["year"] = obj.year_display()
        jurisdiction = obj.state_display().lower()
        if obj.state == AUS:
            used_map = field_map
        else:
            used_map = field_map_states
        for model_field, rds_field in used_map.items():
            kwargs[jurisdiction + "_" + rds_field] = unicode(getattr(obj, model_field))
        add_rawdatarecord(rds, sort_order, **kwargs)
    return messages

def populate_raw_data_nostate(widget_url, label, rds_url,
                    model, field_map):
    messages = []
    rds = get_rawdataset(widget_url, label, rds_url)
    clear_rawdataset(rds)
    sort_order = 1
    for obj in model.objects.all().filter(state=AUS).order_by("year", "financial_year"):
        kwargs = {
            "year": obj.year_display()
        }
        for model_field, rds_field in field_map.items():
            kwargs[rds_field] = unicode(getattr(obj, model_field))
        add_rawdatarecord(rds, sort_order, **kwargs)
        sort_order += 1
    return messages

def update_graph_data(wurl, wlbl, graphlbl, model, field,
                            jurisdictions = None,
                            benchmark_start=None,
                            benchmark_end=None,
                            benchmark_gen=lambda x: x,
                            use_error_bars=False,
                            verbosity=0,
                            pval=None):
    messages=[]
    g = get_graph(wurl, wlbl, graphlbl)
    clear_graph_data(g, pval=pval)
    if jurisdictions:
        qry = model.objects.filter(state__in=jurisdictions)
    else:
        qry = model.objects.all()
    benchmark_init = None
    benchmark_final = None
    for o in qry:
        value = getattr(o,field)
        if callable(value):
            value = value()
        if o.state == AUS and o.float_year() == benchmark_start:
            benchmark_init = value
            benchmark_final = benchmark_gen(benchmark_init)
        kwargs = {}
        kwargs["horiz_value"] = o.year_as_date()
        if use_error_bars:
            kwargs["val_min"] = value-o.uncertainty
            kwargs["val_max"] = value+o.uncertainty
        if jurisdictions and o.state != AUS:
            dataset_url = "state"
        else:
            dataset_url = o.state_display().lower()
        if pval is not None:
            kwargs["pval"] = pval
        add_graph_data(g, dataset_url,
                value,
                **kwargs)
    if benchmark_init is not None and benchmark_final is not None :
        add_graph_data(g, "benchmark",
                    benchmark_init,
                    horiz_value=float_year_as_date(benchmark_start),
                    pval=pval)
        add_graph_data(g, "benchmark",
                    benchmark_final,
                    horiz_value=float_year_as_date(benchmark_end),
                    pval=pval)
    if verbosity > 1:
        if pval:
            messages.append("Graph %s (%s) updated" % (graphlbl, pval.parameters()["state_abbrev"]))
        else:
            messages.append("Graph %s updated" % graphlbl)
    return messages

txt_block_template = Template("""<div class="coag_description">
    <div class="coag_desc_heading">
    {{ benchmark }}
    </div>
    <div class="coag_desc_body">
        {% for body_elem in desc.body %}
            <p>{{ body_elem }}</p>
        {% endfor %}
        {% for body_elem in additional_body %}
            <p>{{ body_elem }}</p>
        {% endfor %}
        {% for inf_elem in desc.influences %}
            <p>
                {% if forloop.first %}
                    <b>Influences:</b>
                {% endif %}
                {{ inf_elem }}
            </p>
        {% endfor %}
        {% for other_elem in desc.other %}
            <p>
                {% if forloop.first %}
                    <b>Other Benchmarks/Indicators:</b>
                {% endif %}
                {{ other_elem }}
            </p>
        {% endfor %}
        {% if state_content %}
            {% for sc_elem in state_content %}
                <p>{{ sc_elem }}</p>
            {% endfor %}
        {% endif %}
    </div>
    <div class="coag_desc_notes">
        <p>Notes:</p>
        <ol>
            {% for note in desc.notes %}
                <li>{{ note }}</li>
            {% endfor %}
        </ol>
    </div>
</div>""")

def update_stats(desc, benchmark, 
                wurl_hero, wlbl_hero, 
                wurl_hero_state, wlbl_hero_state,
                wurl, wlbl, 
                wurl_state, wlbl_state,
                verbosity=0,
                additional_desc_body="additional_body"):
    messages = []
    if wurl_hero:
        set_statistic_data(wurl_hero, wlbl_hero,
                    "status_header",
                    desc["status"]["short"],
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
        set_actual_frequency_display_text(wurl_hero, wlbl_hero,
                    "%s" % unicode(desc["updated"]))
    if wurl_hero_state:
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            set_statistic_data(wurl_hero_state, wlbl_hero_state,
                        "status_header",
                        "Australia - " + desc["status"]["short"],
                        traffic_light_code=desc["status"]["tlc"],
                        icon_code=desc["status"]["icon"],
                        pval=pval)
            set_actual_frequency_display_text(wurl_hero_state, wlbl_hero_state,
                        "%s" % unicode(desc["updated"]),
                        pval=pval)
    if wurl:
        set_statistic_data(wurl, wlbl,
                        "status_header",
                        desc["status"]["short"],
                        traffic_light_code=desc["status"]["tlc"],
                        icon_code=desc["status"]["icon"])
        set_statistic_data(wurl, wlbl,
                        "status_short",
                        desc["status"]["short"],
                        traffic_light_code=desc["status"]["tlc"],
                        icon_code=desc["status"]["icon"])
        set_statistic_data(wurl, wlbl,
                        "status_long",
                        desc["status"]["long"],
                        traffic_light_code=desc["status"]["tlc"])
        set_actual_frequency_display_text(wurl, wlbl,
                    "Updated: %s" % unicode(desc["updated"]))
        set_text_block(wurl, wlbl,
                    txt_block_template.render(Context({ 
                                    "benchmark": desc.get("measure", benchmark), 
                                    "additional_body": desc.get(additional_desc_body),
                                    "desc": desc,
                                    "state": "Australia",
                                    "state_content": desc.get("australia") })))
    if wurl_state:
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            set_statistic_data(wurl_state, wlbl_state,
                            "status_header",
                            "Australia - " + desc["status"]["short"],
                            traffic_light_code=desc["status"]["tlc"],
                            icon_code=desc["status"]["icon"],
                            pval=pval)
            set_statistic_data(wurl_state, wlbl_state,
                            "status_short",
                            "Australia - " + desc["status"]["short"],
                            traffic_light_code=desc["status"]["tlc"],
                            icon_code=desc["status"]["icon"],
                            pval=pval)
            set_statistic_data(wurl_state, wlbl_state,
                            "status_long",
                            desc["status"]["long"],
                            traffic_light_code=desc["status"]["tlc"],
                            pval=pval)
            set_actual_frequency_display_text(wurl_state, wlbl_state,
                        "Updated: %s" % unicode(desc["updated"]),
                        pval=pval)
            st_abbrev = pval.parameters()["state_abbrev"]
            set_text_block(wurl_state, wlbl_state,
                        txt_block_template.render(Context({ 
                                        "benchmark": benchmark, 
                                        "additional_body": desc.get(additional_desc_body),
                                        "desc": desc,
                                        "state": st_abbrev,
                                        "state_content": desc.get(st_abbrev.lower()) })),
                        pval=pval)
    if verbosity > 1:
        messages.append("Stats updated")
    return messages

def update_state_stats(wurl_hero, wlbl_hero, wurl_dtl, wlbl_dtl,
                    model, fields,
                    want_increase=True,
                    override_status=None,
                    verbosity=0):
    messages = []
    p = Parametisation.objects.get(url="state_param")
    for pval in p.parametisationvalue_set.all():
        state_abbrev = pval.parameters()["state_abbrev"]
        state_num = state_map[state_abbrev]
        if override_status:
            status = indicator_statuses[override_status]
        else:
            qry = model.objects.filter(state=state_num).order_by("year")
            reference = qry.first()
            measure = qry.last()
            if reference is None:
                if verbosity > 1:
                    messages.append("%s: No data" % state_abbrev)
                status = indicator_statuses["no_data"]
            elif reference == measure:
                status = indicator_statuses["new_indicator"]
                if verbosity > 1:
                    messages.append("%s: New indicator" % state_abbrev)
            else:
                statuses = []
                for flds in fields:
                    field = flds[0]
                    uncertainty_field = flds[1]
                    if len(flds) > 2:
                        rse_field = flds[2]
                    else:
                        rse_field = None
                    val_1 = getattr(reference, field)
                    val_2 = getattr(measure, field)
                    if callable(val_1):
                        val_1 = val_1()
                    if callable(val_2):
                        val_2 = val_2()
                    diff = val_2 - val_1
                    if isinstance(diff, float):
                        diff = Decimal(diff).quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)
                    if isinstance(diff, int):
                        diff = Decimal(diff)
                    if rse_field:
                        err_1 = float(getattr(reference, rse_field)) / 100.0
                        err_2 = float(getattr(measure, rse_field)) / 100.0
                        val_1r = float(val_1) / 100.0
                        val_2r = float(val_2) / 100.0
                        significance = math.sqrt(
                                    math.pow(val_1r * err_1, 2) 
                                    + math.pow(val_2r * err_2, 2)
                        )
                        test_stat = float(diff)/100.0/significance
                        significant = abs(test_stat) > 1.96
                        if not significant:
                            statuses.append("no_improvement")
                        elif (want_increase and diff == abs(diff)) or (not want_increase and diff != abs(diff)):
                            statuses.append("improving")
                        else:
                            statuses.append("negative_change")
                    else:
                        if uncertainty_field:
                            err_1 = getattr(reference, uncertainty_field)
                            err_2 = getattr(measure, uncertainty_field)
                            total_err = err_1 + err_2
                        else:
                            total_err = Decimal("0.0")
                        if abs(diff) < total_err or diff.is_zero():
                            statuses.append("no_improvement")
                        elif (want_increase and diff == abs(diff)) or (not want_increase and diff != abs(diff)):
                            statuses.append("improving")
                        else:
                            statuses.append("negative_change")
                st_so_far = None
                for st in statuses:
                    if not st_so_far:
                        st_so_far = st
                    elif st_so_far != st:
                        st_so_far = "mixed_results"
                        break
                status = indicator_statuses[st_so_far]
        if wurl_hero:
            set_statistic_data(wurl_hero, wlbl_hero,
                            "status_header_state",
                            state_abbrev + " - " + status["short"],
                            traffic_light_code=status["tlc"],
                            icon_code=status["icon"],
                            pval=pval)
        if wurl_dtl:
            set_statistic_data(wurl_dtl, wlbl_dtl,
                        "status_short_state",
                        state_abbrev + " - " + status["short"],
                        traffic_light_code=status["tlc"],
                        icon_code=status["icon"],
                        pval=pval)
            set_statistic_data(wurl_dtl, wlbl_dtl,
                        "status_header_state",
                        state_abbrev + " - " + status["short"],
                        traffic_light_code=status["tlc"],
                        icon_code=status["icon"],
                        pval=pval)
    return messages

def indicator_tlc_trend(ref_val, val):
    if ref_val < val:
        return ("improving", 1)
    elif ref_val > val:
        return ("negative_change", -1)
    else:
        return ("no_improvement", 0)

