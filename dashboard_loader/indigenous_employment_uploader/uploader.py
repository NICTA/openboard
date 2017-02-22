#   Copyright 2017 CSIRO
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
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from indigenous_employment_uploader.models import *
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
                            ('A', 'Year or financial year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Trajectory point" or "Proportion employed (%)" or "Confidence interval" or "Non-Indigenous")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Set of rows per year, one for each row discriminator included for the year.'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'A year must contain either "Proportion employed (%)", "Confidence interval" and "Non-Indigenous"; or only "Trajectory point"; or all 4 discriminators.',
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
                            ('Desc body', 'Body of benchmark status description. One paragraph per line.'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
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
                                "Indigenous", "Employment",
                                None, IndigenousEmploymentData,
                                {}, {
                                    "indigenous": "Proportion employed (%)",
                                    "indigenous_uncertainty": "Confidence interval",
                                    "non_indigenous": "Non-Indigenous",
                                    "trajectory_point": "Trajectory point",
                                },
                                optional_rows = [
                                    "indigenous",
                                    "indigenous_uncertainty",
                                    "non_indigenous",
                                    "trajectory_point",
                                ],
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "indig_employment-indigenous-hero", "indig_employment-indigenous-hero", 
                                "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                                "indigenous_indig_employment", "indigenous_indig_employment",
                                "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                                verbosity))
        latest_aust = IndigenousEmploymentData.objects.filter(state=AUS, indigenous__isnull=False).last()
        latest_year = latest_aust.year
        if latest_year == 2018:
            complete = True
        else:
            complete = False
        messages.extend(update_state_stats(
                    "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                    "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                    IndigenousEmploymentData, [],
                    use_benchmark_tls=True,
                    status_func=IndigenousEmploymentData.benchmark_tlc,
                    status_func_kwargs={"complete": complete},
                    query_filter_kwargs={"indigenous__isnull": False},
                    )
        )
        messages.extend(
                update_my_graph_data(
                        "indig_employment-indigenous-hero", "indig_employment-indigenous-hero", 
                        "indigenous-indig_employment-hero-graph")
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_indig_employment", "indigenous_indig_employment",
                        "indigenous_indig_employment_summary_graph")
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_indig_employment", "indigenous_indig_employment",
                        "indigenous_indig_employment_detail_graph",
                        use_error_bars=True)
        )
        messages.extend(
                update_state_graph(
                        "indigenous_indig_employment", "indigenous_indig_employment",
                        "indigenous_indig_employment_state_graph",
                        latest_year)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_indig_employment", "indigenous_indig_employment",
                        "indigenous_indig_employment", IndigenousEmploymentData, 
                        {
                            "indigenous": "indigenous",
                            "indigenous_uncertainty": "indigenous_ci",
                            "non_indigenous": "non_indigenous",
                        })
        )
        messages.extend(
                populate_crosstab_raw_data(
                        "indigenous_indig_employment", "indigenous_indig_employment",
                        "data_table", IndigenousEmploymentData, 
                        {
                            "indigenous": "indigenous",
                            "non_indigenous": "non_indigenous",
                        })
        )
        p = Parametisation.objects.get(url="state_param")
        earliest_aust = IndigenousEmploymentData.objects.filter(state=AUS, indigenous__isnull=False).first()
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            latest_state = IndigenousEmploymentData.objects.filter(state=state_num, indigenous__isnull=False).last()
            earliest_state = IndigenousEmploymentData.objects.filter(state=state_num, indigenous__isnull=False).first()
            set_statistic_data(
                    "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                    'non_indigenous',
                    latest_aust.non_indigenous,
# trend=cmp(latest_aust.non_indigenous, earliest_aust.non_indigenous),
                    pval=pval)
            set_statistic_data(
                    "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                    'indigenous',
                    latest_aust.indigenous,
                    traffic_light_code=latest_aust.benchmark_tlc(complete),
# trend=cmp(latest_aust.indigenous, earliest_aust.indigenous),
                    pval=pval)
            set_statistic_data(
                    "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                    'non_indigenous',
                    latest_aust.non_indigenous,
# trend=cmp(latest_aust.non_indigenous, earliest_aust.non_indigenous),
                    pval=pval)
            set_statistic_data(
                    "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                    'indigenous',
                    latest_aust.indigenous,
                    traffic_light_code=latest_aust.benchmark_tlc(complete),
# trend=cmp(latest_aust.indigenous, earliest_aust.indigenous),
                    pval=pval)
 
            set_statistic_data(
                    "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                    'non_indigenous_state',
                    latest_state.non_indigenous,
# trend=cmp(latest_state.non_indigenous, earliest_state.non_indigenous),
                    pval=pval)
            set_statistic_data(
                    "indig_employment-indigenous-hero-state", "indig_employment-indigenous-hero-state", 
                    'indigenous_state',
                    latest_state.indigenous,
                    traffic_light_code=latest_state.benchmark_tlc(complete),
# trend=cmp(latest_state.indigenous, earliest_state.indigenous),
                    pval=pval)
            set_statistic_data(
                    "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                    'non_indigenous_state',
                    latest_state.non_indigenous,
# trend=cmp(latest_state.non_indigenous, earliest_state.non_indigenous),
                    pval=pval)
            set_statistic_data(
                    "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                    'indigenous_state',
                    latest_state.indigenous,
                    traffic_light_code=latest_state.benchmark_tlc(complete),
# trend=cmp(latest_state.indigenous, earliest_state.indigenous),
                    pval=pval)
            messages.extend(
                    update_my_graph_data(
                            "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                            "indigenous_indig_employment_detail_graph",
                            use_error_bars=True,
                            state_num=state_num,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                            "indigenous_indig_employment", IndigenousEmploymentData, 
                            {
                                "indigenous": "indigenous",
                                "indigenous_uncertainty": "indigenous_ci",
                                "non_indigenous": "non_indigenous",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "indigenous_indig_employment_state", "indigenous_indig_employment_state",
                            "data_table", IndigenousEmploymentData, 
                            {
                                "indigenous": "indigenous",
                                "non_indigenous": "non_indigenous",
                            },
                            pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_graph_data(wurl, wlbl, graph, 
                use_error_bars=False, state_num=0, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    qry = IndigenousEmploymentData.objects
    if state_num:
        qry=qry.filter(state__in=[AUS, state_num])
    else:
        qry=qry.filter(state=AUS)
    for i in qry:
        if i.state == AUS:
            suffix = ""
        else:
            suffix = "_state"
        if i.indigenous:
            kwargs = {
                    "horiz_value": i.year_as_date(),
                    "pval": pval
            }
            if use_error_bars:
                kwargs["val_min"]= i.indigenous - i.indigenous_uncertainty
                kwargs["val_max"]= i.indigenous + i.indigenous_uncertainty
            add_graph_data(g, "indigenous" + suffix, i.indigenous, **kwargs)
            add_graph_data(g, "non_indigenous" + suffix, i.non_indigenous,
                    horiz_value=i.year_as_date(),
                    pval=pval)
        if i.trajectory_point:
            add_graph_data(g, "benchmark" + suffix, i.trajectory_point, 
                    horiz_value=i.year_as_date(),
                    pval=pval)
    return messages

def update_state_graph(wurl, wlbl, graph, latest_year):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g)
    for i in IndigenousEmploymentData.objects.filter(year=latest_year):
        add_graph_data(g, "indigenous", i.indigenous,
                            val_min = i.indigenous - i.indigenous_uncertainty,
                            val_max = i.indigenous + i.indigenous_uncertainty,
                            cluster = i.state_display().lower())
        add_graph_data(g, "non_indigenous", i.non_indigenous,
                            cluster = i.state_display().lower())
    return messages
