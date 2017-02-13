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
from indigenous_yr12_uploader.models import *
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
                            ('B', 'Row Discriminator ("Trajectory" or "Actual"'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Set of rows per year, one for each row discriminator included for the year.'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Trajectory and Actual are both optional, but at least one must be supplied for each year in the file.',
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
                                "Indigenous", "Yr12 Attainment",
                                None, IndigenousYr12Data,
                                {}, {
                                    "indigenous_attainment": "Actual",
                                    "indigenous_trajectory": "Trajectory",
                                },
                                optional_rows = [
                                    "indigenous_attainment",
                                    "indigenous_trajectory",
                                ],
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "indig_yr12-indigenous-hero", "indig_yr12-indigenous-hero", 
                                "indig_yr12-indigenous-hero-state", "indig_yr12-indigenous-hero-state", 
                                "indigenous_yr12", "indigenous_yr12",
                                "indigenous_yr12_state", "indigenous_yr12_state",
                                verbosity))
        latest_aust = IndigenousYr12Data.objects.filter(indigenous_attainment__isnull=False, state=AUS).last()
        latest_year = latest_aust.year
        if latest_year == 2020:
            complete = True
        else:
            complete = False
        messages.extend(update_state_stats(
                    "indig_yr12-indigenous-hero-state", "indig_yr12-indigenous-hero-state", 
                    "indigenous_yr12_state", "indigenous_yr12_state",
                    IndigenousYr12Data, [],
                    use_benchmark_tls=True,
                    status_func=IndigenousYr12Data.benchmark_tlc,
                    status_func_kwargs={"complete": complete},
                    query_filter_kwargs={"indigenous_attainment__isnull": False},
                    verbosity=verbosity,
                    )
        )
        messages.extend(
                update_my_graph_data(
                        "indig_yr12-indigenous-hero", "indig_yr12-indigenous-hero", 
                        "indigenous-yr12-hero-graph")
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_yr12", "indigenous_yr12",
                        "indigenous_yr12_summary_graph")
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_yr12", "indigenous_yr12",
                        "indigenous_yr12_detail_graph",
                        all_states=True)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_yr12", "indigenous_yr12",
                        "indigenous_yr12", IndigenousYr12Data, 
                        {
                            "indigenous_attainment": "indigenous",
                            "indigenous_trajectory": "indigenous_trajectory",
                        })
        )
        messages.extend(
                populate_crosstab_raw_data(
                        "indigenous_yr12", "indigenous_yr12",
                        "data_table", IndigenousYr12Data, 
                        {
                            "attainment_display": "indigenous",
                            "trajectory_display": "trajectory",
                        })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                    update_my_graph_data(
                            "indig_yr12-indigenous-hero-state", "indig_yr12-indigenous-hero-state", 
                            "indigenous-yr12-hero-graph",
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    update_my_graph_data(
                            "indigenous_yr12_state", "indigenous_yr12_state",
                            "indigenous-yr12-summary-graph",
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    update_my_graph_data(
                            "indigenous_yr12_state", "indigenous_yr12_state",
                            "indigenous-yr12-detail-graph",
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_yr12_state", "indigenous_yr12_state",
                            "indigenous_yr12", IndigenousYr12Data, 
                            {
                                "indigenous_attainment": "indigenous",
                                "indigenous_trajectory": "indigenous_trajectory",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "indigenous_yr12_state", "indigenous_yr12_state",
                            "data_table", IndigenousYr12Data, 
                            {
                                "attainment_display": "indigenous",
                                "trajectory_display": "trajectory",
                            },
                            pval=pval)
            )

    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_graph_data(wurl, wlbl, graph, 
                all_states=False, state_num=0, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    qry = IndigenousYr12Data.objects
    if all_states:
        qry=qry.all()
    elif state_num:
        qry=qry.filter(state__in=[AUS, state_num])
    else:
        qry=qry.filter(state=AUS)
    for i in qry:
        if i.indigenous_attainment:
            if i.state != AUS and state_num:
                ds = "state"
            else:
                ds = i.state_display().lower()
            add_graph_data(g, ds, i.indigenous_attainment, 
                            horiz_value=i.year_as_date(), pval=pval)
        if i.indigenous_trajectory and (i.state == AUS or (not all_states and state_num==i.state)):
            if i.state == AUS:
                ds = "benchmark"
            else:
                ds = "benchmark_state"
            add_graph_data(g, ds, i.indigenous_trajectory, 
                    horiz_value=i.year_as_date(),
                    pval=pval)
    return messages

