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
from indigenous_school_attendance_uploader.models import *
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
                            ('B', 'Row Discriminator ("Trajectory point" or "Student attendance rate (%)"'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Set of rows per year, one for each row discriminator included for the year.'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'The "Trajectory point" is expected to be supplied for the first and last years in the file, but is otherwise optional.',
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
                                "Indigenous", "School attendance",
                                None, IndigenousSchoolAttendanceData,
                                {}, {
                                    "indigenous_attendance": "Student attendance rate (%)",
                                    "indigenous_trajectory": "Trajectory point",
                                },
                                optional_rows = [
                                    "indigenous_trajectory",
                                ],
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "school_attendance-indigenous-hero", "school_attendance-indigenous-hero", 
                                "school_attendance-indigenous-hero-state", "school_attendance-indigenous-hero-state", 
                                "indigenous_school_attendance", "indigenous_school_attendance",
                                "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                                verbosity))
        latest_aust = IndigenousSchoolAttendanceData.objects.filter(state=AUS).last()
        reference_aust = IndigenousSchoolAttendanceData.objects.filter(state=AUS).first()
        latest_year = latest_aust.year
        reference_year = reference_aust.year
        if latest_year == 2019:
            complete = True
        else:
            complete = False
        messages.extend(update_state_stats(
                    "school_attendance-indigenous-hero-state", "school_attendance-indigenous-hero-state", 
                    "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                    IndigenousSchoolAttendanceData, [],
                    use_benchmark_tls=True,
                    status_func=IndigenousSchoolAttendanceData.benchmark_tlc,
                    status_func_kwargs={"complete": complete},
                    )
        )
        messages.extend(
                update_my_graph_data(
                        "school_attendance-indigenous-hero", "school_attendance-indigenous-hero", 
                        "indigenous-school_attendance-hero-graph",
                        reference_year, latest_year)
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_school_attendance", "indigenous_school_attendance",
                        "indigenous_school_attendance_summary_graph",
                        reference_year, latest_year)
        )
        messages.extend(
                update_my_graph_data(
                        "indigenous_school_attendance", "indigenous_school_attendance",
                        "indigenous_school_attendance_detail_graph",
                        reference_year, latest_year,
                        all_states=True)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_school_attendance", "indigenous_school_attendance",
                        "indigenous_school_attendance", IndigenousSchoolAttendanceData, 
                        {
                            "indigenous_attendance": "indigenous",
                            "indigenous_trajectory": "indigenous_trajectory",
                        })
        )
        messages.extend(
                populate_crosstab_raw_data(
                        "indigenous_school_attendance", "indigenous_school_attendance",
                        "data_table", IndigenousSchoolAttendanceData, 
                        {
                            "attendance_display": "indigenous",
                            "trajectory_display": "trajectory",
                        })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                    update_my_graph_data(
                            "school_attendance-indigenous-hero-state", "school_attendance-indigenous-hero-state", 
                            "indigenous-school_attendance-hero-graph",
                            reference_year, latest_year,
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    update_my_graph_data(
                            "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                            "indigenous-school_attendance-summary-graph",
                            reference_year, latest_year,
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    update_my_graph_data(
                            "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                            "indigenous-school_attendance-detail-graph",
                            reference_year, latest_year,
                            state_num = state_num,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                            "indigenous_school_attendance", IndigenousSchoolAttendanceData, 
                            {
                                "indigenous_attendance": "indigenous",
                                "indigenous_trajectory": "indigenous_trajectory",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "indigenous_school_attendance_state", "indigenous_school_attendance_state",
                            "data_table", IndigenousSchoolAttendanceData, 
                            {
                                "attendance_display": "indigenous",
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
                ref_year, latest_year, 
                all_states=False, state_num=0, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    qry = IndigenousSchoolAttendanceData.objects.filter(year__in=(ref_year, latest_year))
    if all_states:
        qry=qry
    elif state_num:
        qry=qry.filter(state__in=[AUS, state_num])
    else:
        qry=qry.filter(state=AUS)
    for i in qry:
        if i.state != AUS and state_num:
            cluster = "state"
        else:
            cluster = i.state_display().lower()
        if i.year == ref_year:
            ds = "reference_year"
        else:
            ds = "latest_year"
        add_graph_data(g, ds, i.indigenous_attendance, 
                        cluster=cluster, pval=pval)
        if i.year == latest_year:
            add_graph_data(g, "benchmark", i.indigenous_trajectory, 
                    cluster=cluster,
                    pval=pval)
    set_dataset_override(g, "reference_year", unicode(ref_year), pval=pval)
    set_dataset_override(g, "latest_year", unicode(latest_year), pval=pval)
    set_dataset_override(g, "benchmark", "%s Trajectory" % latest_year, pval=pval)
    return messages

