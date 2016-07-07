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

# These are the names of the groups that have permission to upload data for this uploader.
# If the groups do not exist they are created on registration.
groups = [ "upload_all", "upload_coag" ]

# This describes the file format.  It is used to describe the format by both
# "python manage.py upload_data frontlineservice_uploader" and by the uploader 
# page in the data admin GUI.
file_format = {
    "format": "xlsx",
    "sheets": [
         {
             "name": "Table of Contents",
             "rows": [],
             "cols": [],
             "notes": [ "Not read by uploader", ],
         },
         {
             "name": "1 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "2 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "3 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "4 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "5 NASWD",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "6 NASWD",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "7 NASWD",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
    ],
}

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(load_housing_data(wb, verbosity))
        messages.extend(load_skills_data(wb, verbosity))
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def load_housing_data(wb, verbosity):
    messages = []
    if verbosity > 1:
        messages.append("Loading Housing Data...")
    messages.extend(load_housing_rental_stress(wb, verbosity))
    messages.extend(load_housing_homelessness(wb, verbosity))
    messages.extend(load_housing_indigenous_ownership(wb, verbosity))
    messages.extend(load_housing_indigenous_crowding(wb, verbosity))
    return messages

def load_skills_data(wb, verbosity):
    messages = []
    if verbosity > 1:
        messages.append("Loading Skills Data...")
    messages.extend(load_skills_qualifications(wb, verbosity))
    messages.extend(load_skills_higher_qualifications(wb, verbosity))
    messages.extend(load_skills_vet_employment(wb, verbosity))
    return messages

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
    for col in column_labels(sheet.min_column, sheet.max_column):
       val = sheet["%s%d" % (col, row)].value
       if val in state_map:
            state_cols[state_map[val]] = col
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
        first_cell=sheet["A%d" % row].value
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

def calculate_benchmark(reference_year, target_year, 
                    target, desire_overtarget, 
                    model, benchmark_field, 
                    widget_url, widget_label, 
                    verbosity):
    messages = []
    metrics = [ (obj.float_year(), float(getattr(obj,benchmark_field))) for obj in model.objects.filter(state=AUS).order_by("year", "financial_year") ]
    trend = find_trend(metrics, reference_year, target_year)
    if trend:
        benchmark = trend["benchmark"]*100.0
        datum = trend["datum"]
        reference = trend["reference"]
        if (desire_overtarget and trend["benchmark"] >= target) or (not desire_overtarget and trend["benchmark"] <= target):
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

def load_housing_rental_stress(wb, verbosity):
    messages = []
    messages.extend(load_state_grid(wb, "1 NAHA", 
                        "Housing", "Rental Stress", 
                        "Notes:", HousingRentalStressData,
                        {}, {"percentage": "%", "uncertainty": "+"}, 
                        verbosity))
    messages.extend(calculate_benchmark(2007.5, 2015.5, 
                            -0.1, False, 
                            HousingRentalStressData, "percentage", 
                            "rental_stress", "rental_stress", 
                            verbosity))
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
    return messages

