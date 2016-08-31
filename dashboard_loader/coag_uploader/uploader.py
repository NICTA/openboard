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
from scipy import stats
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from widget_def.models import Parametisation, ParametisationValue
from coag_uploader.models import *
from django.template import Template, Context

hero_widgets = {
    "housing": [ 
            "rentalstress-housing-hero", 
            "homelessness-housing-hero", 
            "indigenous_homeownership-housing-hero", 
            "indigenous_overcrowding-housing-hero", 
            "indigenous_remote-housing-hero", 
    ],
}

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

def load_state_grid(wb, sheet_name, data_category, dataset, abort_on, model, first_cell_rows, intermediate_cell_rows, verbosity, transforms={}):
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
            if first_cell == abort_on:
                break
            first_cell_matched = False
            for fld, fcr in first_cell_rows.items():
                if first_cell == fcr:
                    first_cell_matched=True
                    rows[fld] = row
                    break
            if not first_cell_matched:
                try:
                    (year, isfy) = parse_year(first_cell)
                    zero_all_rows(rows)
                except:
                    pass
        if year:
            for col in column_labels(2, sheet.max_column):
                if col in state_cols.values():
                    break
                cval = sheet["%s%d" % (col, row)].value
                for fld, icr in intermediate_cell_rows.items():
                    if cval == icr:
                        rows[fld]=row
                        break

                if year and all_rows_found(rows):
                    for state, scol in state_cols.items():
                        defaults = { "financial_year": isfy }
                        for fld, frow in rows.items():
                            rawval = sheet["%s%d" % (scol, frow)].value
                            if fld in transforms:
                                defaults[fld] = transforms[fld](rawval)
                            else:
                                defaults[fld] = rawval
                        obj, created = model.objects.update_or_create(
                                    state=state,
                                    year=year,
                                    defaults=defaults)
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

def load_benchmark_description(wb, sheetname, indicator=False):
    key_lookup = {
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
    }
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
    }
    sheet = wb[sheetname]
    desc = {}
    append_to = None
    row = 1
    if indicator:
        statuses = indicator_statuses
    else:
        statuses = benchmark_statuses
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
        if not key:
            append_to.append(value)
        row += 1
    return desc

def populate_raw_data(widget_url, label, rds_url,
                    model, field_map):
    messages = []
    rds = get_rawdataset(widget_url, label, rds_url)
    clear_rawdataset(rds)
    sort_order = 1
    for obj in model.objects.all().order_by("state", "year", "financial_year"):
        kwargs = {
            "jurisdiction": obj.state_display(),
            "year": obj.year_display()
        }
        for model_field, rds_field in field_map.items():
            kwargs[rds_field] = unicode(getattr(obj, model_field))
        add_rawdatarecord(rds, sort_order, **kwargs)
        sort_order += 1
    return messages

def populate_crosstab_raw_data(widget_url, label, rds_url,
                    model, field_map):
    messages = []
    rds = get_rawdataset(widget_url, label, rds_url)
    clear_rawdataset(rds)
    sort_order = 1
    kwargs = {}
    kwargs["year"] = None
    for obj in model.objects.all().order_by("year", "financial_year", "state"):
        if obj.year_display() != kwargs["year"]:
            add_rawdatarecord(rds, sort_order, **kwargs)
            sort_order += 1
            kwargs = {}
            kwargs["year"] = obj.year_display()
        jurisdiction = obj.state_display().lower()
        for model_field, rds_field in field_map.items():
            kwargs[jurisdiction + "_" + rds_field] = unicode(getattr(obj, model_field))
    add_rawdatarecord(rds, sort_order, **kwargs)
    return messages

def update_graph_data(wurl, wlbl, graphlbl, model, field,
                            jurisdictions = None,
                            benchmark_start=None,
                            benchmark_end=None,
                            benchmark_gen=lambda x: x,
                            use_error_bars=False,
                            verbosity=0):
    messages=[]
    g = get_graph(wurl, wlbl, graphlbl)
    clear_graph_data(g)
    if jurisdictions:
        qry = model.objects.filter(state__in=jurisdictions)
    else:
        qry = model.objects.all()
    benchmark_init = None
    benchmark_final = None
    for o in qry:
        value = getattr(o,field)
        if o.state == AUS and o.float_year() == benchmark_start:
            benchmark_init = value
            benchmark_final = benchmark_gen(benchmark_init)
        kwargs = {}
        kwargs["horiz_value"] = o.year_as_date()
        if use_error_bars:
            kwargs["val_min"] = value-o.uncertainty
            kwargs["val_max"] = value+o.uncertainty
        add_graph_data(g, o.state_display().lower(),
                value,
                **kwargs)
    if benchmark_init is not None and benchmark_final is not None :
        add_graph_data(g, "benchmark",
                    benchmark_init,
                    horiz_value=float_year_as_date(benchmark_start))
        add_graph_data(g, "benchmark",
                    benchmark_final,
                    horiz_value=float_year_as_date(benchmark_end))
    if verbosity > 1:
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
    </div>
    <div class="coag_desc_notes">'
        <p>Notes:</p>
        <ol>
            {% for note in desc.notes %}
                <li>{{ note }}</li>
            {% endfor %}
        </ol>
    </div>
</div>""")

def update_stats(desc, section, hero_indicator_url, benchmark, wurl_hero, wlbl_hero, wurl, wlbl, verbosity):
    messages = []
    for w in hero_widgets[section]:
        set_statistic_data(w, w, hero_indicator_url, None, 
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
    if wurl_hero:
        set_statistic_data(wurl_hero, wlbl_hero,
                    "status_header",
                    desc["status"]["short"],
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
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
                                "benchmark": benchmark, 
                                "desc": desc })))
    if verbosity > 1:
        messages.append("Stats updated")
    return messages

def load_housing_homelessness(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "2 NAHA", 
                        "Housing", "Homelessness", 
                        "Notes:", HousingHomelessData,
                        {
                            "homeless_persons": "All homeless persons", 
                            "rate_per_10k": "Rate per 10,000 of the population"
                        }, 
                        { "percent_of_national": "%",}, verbosity))
    messages.extend(calculate_benchmark(2006.0, 2013.0,
                            -0.07, False,
                            HousingHomelessData, "homeless_persons",
                            "homelessness", "homelessness", 
                            verbosity))
    messages.extend(populate_raw_data("homelessness", "homelessness",
                        "homelessness_data", HousingHomelessData,
                        {
                            "homeless_persons": "number_homeless_persons",
                            "percent_of_national": "proportion_national_total",
                            "rate_per_10k": "rate_per_10k",
                        }))
    return messages

def load_housing_indigenous_ownership(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "3 NAHA", 
                        "Housing", "Indigenous Ownership", 
                        "Notes:", IndigenousHomeOwnershipData,
                        { "uncertainty": "95 per cent confidence interval"}, 
                        { "percentage": "%"}, verbosity))
    messages.extend(calculate_benchmark(2008.0, 2017.5,
                            0.1, True,
                            IndigenousHomeOwnershipData, "percentage",
                            "indigenous_home_ownership", "indigenous_home_ownership", 
                            verbosity))
    messages.extend(populate_raw_data("indigenous_home_ownership", 
                        "indigenous_home_ownership",
                        "indigenous_home_ownership_data", 
                        IndigenousHomeOwnershipData,
                        {
                            "percentage": "indigenous_home_ownership_rate",
                            "uncertainty": "uncertainty",
                        }))
    return messages

def load_housing_indigenous_crowding(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "4 NAHA", 
                        "Housing", "Indigenous Overcrowding", 
                        "Notes:", IndigenousOvercrowdingData,
                        {}, {"percentage": "%", "uncertainty": "+"}, 
                        verbosity))
    messages.extend(calculate_benchmark(2008.0, 2017.5,
                            -0.2, False,
                            IndigenousOvercrowdingData, "percentage",
                            "indigenous_overcrowding", "indigenous_overcrowding", 
                            verbosity))
    messages.extend(populate_raw_data("indigenous_overcrowding", 
                        "indigenous_overcrowding",
                        "indigenous_overcrowding_data", 
                        IndigenousOvercrowdingData,
                        {
                            "percentage": "indigenous_overcrowding",
                            "uncertainty": "uncertainty",
                        }))
    return messages

def load_skills_qualifications(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "5 NASWD",
                        "Skills", "Without Cert III Qualifications",
                        "Notes:", QualificationsData,
                        { "uncertainty": "95 per cent confidence interval"}, 
                        { "percentage": "%"}, verbosity,
                        transforms={ "percentage": lambda x: 100.0-x, }))
    messages.extend(calculate_benchmark(2009.0, 2020.0,
                            -0.5, False,
                            QualificationsData, "percentage",
                            "qualifications", "qualifications",
                            verbosity))
    messages.extend(populate_raw_data("qualifications", "qualifications",
                        "qualifications_data", 
                        QualificationsData,
                        {
                            "percentage": "unqualified_percentage",
                            "uncertainty": "uncertainty",
                        }))
    return messages

def load_skills_higher_qualifications(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "6 NASWD",
                        "Skills", "Higher Qualifications",
                        "Notes:", HigherQualificationsData,
                        { "diploma": "Diploma", "adv_diploma": "Advanced Diploma"}, 
                        {}, verbosity))
    messages.extend(calculate_benchmark(2009.0, 2020.0,
                            1, True,
                            HigherQualificationsData, "total",
                            "higher_qualifications", "higher_qualifications",
                            verbosity))
    messages.extend(populate_raw_data("higher_qualifications", 
                        "higher_qualifications",
                        "higher_qualifications_data", 
                        HigherQualificationsData,
                        {
                            "diploma": "diplomas",
                            "adv_diploma": "advanced_diplomas",
                            "total": "total",
                        }))
    return messages

def load_skills_vet_employment(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "7 NASWD",
                        "Skills", "VET Graduates with Improved Employment",
                        "Source: ", ImprovedVetGraduatesData,
                        { "uncertainty": "95 per cent confidence interval"}, 
                        { "percentage": "%"}, verbosity))
    messages.extend(calculate_indicator(True,
                    ImprovedVetGraduatesData, "percentage",
                    "vet_employment", "vet_employment", verbosity))
    messages.extend(populate_raw_data("vet_employment", 
                        "vet_employment",
                        "vet_employment_data", 
                        ImprovedVetGraduatesData,
                        {
                            "percentage": "vet_grad_improvement",
                            "uncertainty": "uncertainty",
                        }))
    return messages


