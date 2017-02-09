#   Copyright 2016,2017 CSIRO
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
from decimal import Decimal
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from legal_assistance_total_services_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats, indicator_tlc_trend
from widget_def.models import Parametisation

# These are the names of the groups that have permission to upload data for this uploader.
# If the groups do not exist they are created on registration.
groups = [ "upload_all", "upload" ]

# This describes the file format.  It is used to describe the format by both
# "python manage.py upload_data frontlineservice_uploader" and by the uploader 
# page in the data admin GUI.


file_format = {
    "format": "xlsx",
    "sheets": [
            {
                "name": "Data",
                "cols": [ 
                            ('A', '6 month date range in format "Month to Month YYYY", e.g. "January to June 2016"'),
                            ('B', 'Service Type (Must be "Legal aid commissions" or "Community legal centres")'),
                            ('C', 'Unit (Must be "Total representation services delivered to people experiencing financial disadvantage (%)" or "State benchmark")'),
                            ('...', 'Column per state (NB No "Aust" column)'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Four rows per date, one for each possible combination of Service Type and Unit'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Description",
                "cols": [
                            ('A', 'Key'),
                            ('B', 'Value'),
                        ],
                "rows": [
                            ('Measure', 'Full description of benchmark'),
                            ('Short Title', 'Short widget title (not used)'),
                            ('Status', 'Indicator status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of indicator status description. One paragraph per line.'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Legal Assistance", "Total Services",
                                None, LegalAssistData,
                                {}, {
                                    "lac": ("Legal aid commissions", "Total representation services delivered to people experiencing financial disadvantage (%)"),
                                    "clc": ("Community legal centres", "Total representation services delivered to people experiencing financial disadvantage (%)"),
                                    "lac_benchmark": ("Legal aid commissions", "State benchmark"),
                                    "clc_benchmark": ("Community legal centres", "State benchmark"),
                                },
                                verbosity=verbosity,
                                transforms= {
                                    "lac": lambda x: 100.0 * x,
                                    "clc": lambda x: 100.0 * x,
                                    "lac_benchmark": lambda x: 100.0 * x,
                                    "clc_benchmark": lambda x: 100.0 * x,
                                },
                                date_field="start_date",
                                date_parser=sixmonth_parser))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "total_svc-legal-hero", "total_svc-legal-hero", 
                                "total_svc-legal-hero-state", "total_svc-legal-hero-state", 
                                "legal_total_svc", "legal_total_svc", 
                                "legal_total_svc_state", "legal_total_svc_state", 
                                verbosity))
        messages.extend(update_state_stats(
                                "total_svc-legal-hero-state", "total_svc-legal-hero-state", 
                                "legal_total_svc_state", "legal_total_svc_state", 
                                LegalAssistData, [],
                                use_benchmark_tls=True,
                                status_func=LegalAssistData.tlc_overall,
                                verbosity=verbosity
                                ))
        latest_date = LegalAssistData.objects.order_by("start_date").last().start_date
        earliest_date = LegalAssistData.objects.order_by("start_date").last().start_date
        latest_data = LegalAssistData.objects.filter(start_date=latest_date)
        earliest_data = LegalAssistData.objects.filter(start_date=earliest_date)
        clc_states = {}
        lac_states = {}
        ref_clc_met = 0
        ref_lac_met = 0
        for ld in earliest_data:
            sk = state_dict[ld.state]
            clc_states[sk] = {
                "ref_val": ld.clc,
            }
            lac_states[sk] = {
                "ref_val": ld.lac,
            }
            if ld.meets_lac_benchmark():
                ref_lac_met += 1
            if ld.meets_clc_benchmark():
                ref_clc_met += 1
        clc_met = 0
        lac_met = 0
        for ld in latest_data:
            sk = state_dict[ld.state]
            clc_states[sk]["val"] = ld.clc
            lac_states[sk]["val"] = ld.lac
            clc_states[sk]["tlc"] = ld.tlc_clc()
            lac_states[sk]["tlc"] = ld.tlc_lac()
            if ld.meets_lac_benchmark():
                lac_met += 1
            if ld.meets_clc_benchmark():
                clc_met += 1
        set_statistic_data("legal_total_svc", "legal_total_svc",
                        "benchmark_lac", ld.lac_benchmark, traffic_light_code="achieved")
        set_statistic_data("legal_total_svc", "legal_total_svc",
                        "benchmark_clc", ld.clc_benchmark, traffic_light_code="achieved")
        for sk in clc_states.keys():
            trend = cmp(lac_states[sk]["val"], lac_states[sk]["ref_val"])
            set_statistic_data("legal_total_svc", "legal_total_svc",
                            sk.lower()+"_lac", lac_states[sk]["val"], 
                            traffic_light_code=lac_states[sk]["tlc"], trend=trend)
            trend = cmp(clc_states[sk]["val"], clc_states[sk]["ref_val"])
            set_statistic_data("legal_total_svc", "legal_total_svc",
                            sk.lower()+"_clc", clc_states[sk]["val"], 
                            traffic_light_code=clc_states[sk]["tlc"], trend=trend)
        tlc = counts_tlc(lac_met)
        trend = cmp(lac_met, ref_lac_met)
        set_statistic_data("total_svc-legal-hero", "total_svc-legal-hero",
                        "lac", lac_met, traffic_light_code=tlc, trend=trend)
        set_statistic_data("legal_total_svc", "legal_total_svc",
                        "lac", lac_met, traffic_light_code=tlc, trend=trend)
        tlc = counts_tlc(clc_met)
        trend = cmp(clc_met, ref_clc_met)
        set_statistic_data("total_svc-legal-hero", "total_svc-legal-hero",
                        "clc", clc_met, traffic_light_code=tlc, trend=trend)
        set_statistic_data("legal_total_svc", "legal_total_svc",
                        "clc", clc_met, traffic_light_code=tlc, trend=trend)
        messages.extend(
                populate_my_raw_datasets("legal_total_svc", "legal_total_svc")
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            ref = LegalAssistData.objects.get(state=state_num, start_date=earliest_date)
            obj = LegalAssistData.objects.get(state=state_num, start_date=latest_date)
            lac_trend = cmp(obj.lac, ref.lac)
            clc_trend = cmp(obj.clc, ref.clc)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "benchmark_lac", obj.lac_benchmark, 
                        traffic_light_code="achieved",
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "achievement_lac", obj.lac, 
                        traffic_light_code=obj.tlc_lac(), 
                        trend=lac_trend,
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "benchmark_clc", obj.clc_benchmark, 
                        traffic_light_code="achieved",
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "achievement_clc", obj.clc, 
                        traffic_light_code=obj.tlc_clc(), 
                        trend=clc_trend,
                        pval=pval)
            set_statistic_data("legal_total_svc_state", "legal_total_svc_state",
                        "benchmark_lac", obj.lac_benchmark, 
                        traffic_light_code="achieved",
                        pval=pval)
            set_statistic_data("legal_total_svc_state", "legal_total_svc_state",
                        "achievement_lac", obj.lac, 
                        traffic_light_code=obj.tlc_lac(), 
                        trend=lac_trend,
                        pval=pval)
            set_statistic_data("legal_total_svc_state", "legal_total_svc_state",
                        "benchmark_clc", obj.clc_benchmark, 
                        traffic_light_code="achieved",
                        pval=pval)
            set_statistic_data("legal_total_svc_state", "legal_total_svc_state",
                        "achievement_clc", obj.clc, 
                        traffic_light_code=obj.tlc_clc(), 
                        trend=clc_trend,
                        pval=pval)
            messages.extend(
                    populate_my_graph(state_num, pval)
            )
            messages.extend(
                    populate_my_raw_datasets("legal_total_svc_state", "legal_total_svc_state", pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def counts_tlc(val):
    if val  == 8:
        return "achieved"
    elif val == 0:
        return "not_met"
    else:
        return "not_on_track"

def sixmonth_parser(din):
    dbits=din.split()
    if len(dbits) != 4 or dbits[1] != "to":
        return None
    year = int(dbits[3])
    if year < 2000 or year > 3000:
        return None
    if dbits[0] == "July":
        month=7
    elif dbits[0] == "January":
        month=1
    else:
        return None
    return datetime.date(year, month, 1)

def populate_my_graph(state_num, pval):
    messages = []
    g = get_graph("legal_total_svc_state", "legal_total_svc_state", 
                    "legal_total_svc_detail_graph")
    clear_graph_data(g, pval=pval)
    for obj in LegalAssistData.objects.filter(state=state_num).order_by("start_date"):
        add_graph_data(g, "lac", obj.lac, horiz_value=obj.start_date, pval=pval)
        add_graph_data(g, "clc", obj.clc, horiz_value=obj.start_date, pval=pval)

        add_graph_data(g, "lac-benchmark", obj.lac_benchmark, horiz_value=obj.start_date, pval=pval)
        add_graph_data(g, "clc-benchmark", obj.clc_benchmark, horiz_value=obj.start_date, pval=pval)
        add_graph_data(g, "lac-benchmark", obj.lac_benchmark, horiz_value=obj.end_date(), pval=pval)
        add_graph_data(g, "clc-benchmark", obj.clc_benchmark, horiz_value=obj.end_date(), pval=pval)
    return messages

def populate_my_raw_datasets(wurl, wlbl, pval=None):
    messages = []
    rds = get_rawdataset(wurl, wlbl, "legal_total_svc")
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    for obj in LegalAssistData.objects.all().order_by("start_date", "state"):
        kwargs = {
            "jurisdiction": obj.state_display(),
            "date": obj.date_display(),
            "svc_type": "Legal aid commissions",
            "percent": unicode(obj.lac),
            "benchmark": unicode(obj.lac_benchmark)
        }
        add_rawdatarecord(rds, sort_order, pval=pval, **kwargs)    
        sort_order += 1
        kwargs["svc_type"] = "Community legal centres"
        kwargs["percent"] = unicode(obj.clc)
        kwargs["benchmark"] = unicode(obj.clc_benchmark)
        add_rawdatarecord(rds, sort_order, pval=pval, **kwargs)    
        sort_order += 1
    rds = get_rawdataset(wurl, wlbl, "data_table")
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    lac_kwargs = { "date": None }
    clc_kwargs = { "date": None }
    for obj in LegalAssistData.objects.all().order_by("start_date", "state"):
        _date = obj.format_daterange_pretty()
        if _date != lac_kwargs["date"]:
            if lac_kwargs["date"]:
                add_rawdatarecord(rds, sort_order, pval=pval, **lac_kwargs)
                sort_order += 1
                add_rawdatarecord(rds, sort_order, pval=pval, **clc_kwargs)
                sort_order += 1
            lac_kwargs = { 
                    "date": _date, 
                    "svc_type": "Legal aid commissions", 
                    "target_percent": unicode(obj.lac_benchmark)
            }
            clc_kwargs = { 
                    "date": _date , 
                    "svc_type": "Community legal centres",
                    "target_percent": unicode(obj.clc_benchmark)
            }
        jurisdiction = obj.state_display().lower()
        lac_kwargs[jurisdiction + "_percent"] = unicode(obj.lac)
        clc_kwargs[jurisdiction + "_percent"] = unicode(obj.clc)
    add_rawdatarecord(rds, sort_order, pval=pval, **lac_kwargs)
    sort_order += 1
    add_rawdatarecord(rds, sort_order, pval=pval, **clc_kwargs)
    return messages

