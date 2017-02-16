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
from django.db.models import Sum
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from health_mental_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats, column_labels, load_progress_grid
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
                            ('A', 'State'),
                            ('B', 'Project")'),
                            ('C', 'Progress statement'),
                            ('D', 'Status'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "Column Heading row"),
                            ('...', 'Row per project'),
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
                            ('Status', 'Benchmark status'),
                            ('Updated', 'Year data last updated'),
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
        MentalHealthProjects.objects.all().delete()
        messages.extend(
                load_progress_grid(wb, "Data",
                                "Health", "Mental Health Reform",
                                MentalHealthProjects,
                                {
                                    "project": "Project",
                                    "progress": "Progress statement",
                                    "state": "State",
                                    "status": "Status",
                                },
                                transforms = {
                                    "state": lambda x: state_map[x],
                                    "status": lambda x:project_map[x],
                                },
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                            "mental-health-hero", "mental-health-hero", 
                            "mental-health-hero-state", "mental-health-hero-state", 
                            "health_mental", "health_mental", 
                            "health_mental_state", "health_mental_state", 
                            verbosity))
        messages.extend(update_state_stats(
                            "mental-health-hero-state", "mental-health-hero-state", 
                            "health_mental_state", "health_mental_state", 
                            None, [],
                            override_status=desc["status"]["tlc"],
                            use_benchmark_tls = True,
                            verbosity=verbosity))
        proj_count = MentalHealthProjects.objects.all().count()
        set_statistic_data("mental-health-hero", "mental-health-hero",
                            "completed", proj_count,
                            traffic_light_code=desc["status"]["tlc"])
        set_statistic_data("health_mental", "health_mental", 
                            "completed", proj_count,
                            traffic_light_code=desc["status"]["tlc"])
        clear_statistic_list( "health_mental", "health_mental", 
                              "key_projects")
        sort_order = 5
        for kp in MentalHealthProjects.objects.all():
            add_statistic_list_item(
                            "health_mental", "health_mental", 
                            "key_projects",
                            kp.status_display(),
                            sort_order,
                            traffic_light_code = kp.status_tlc(),
                            label="(%s) %s" % (kp.state_display(), kp.project)
            )
            sort_order += 5
        messages.extend(
                populate_raw_data(
                            "health_mental", "health_mental", 
                            "mental_health", MentalHealthProjects, 
                                {
                                    "project": "project",
                                    "progress": "progress_statement",
                                    "status_display": "status",
                                },
                            use_dates=False)
                )
        messages.extend(
                populate_raw_data(
                            "health_mental", "health_mental", 
                            "data_table", MentalHealthProjects, 
                                {
                                    "project": "project",
                                    "progress": "progress_statement",
                                    "status_display": "status",
                                },
                            use_dates=False)
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_count = MentalHealthProjects.objects.filter(state=state_num).count()
            set_statistic_data(
                        "mental-health-hero-state", "mental-health-hero-state",
                        "completed", proj_count,
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "mental-health-hero-state", "mental-health-hero-state",
                        "completed_state", state_count,
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "health_mental_state", "health_mental_state",
                        "completed", proj_count,
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "health_mental_state", "health_mental_state",
                        "completed_state", state_count,
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            clear_statistic_list("health_mental_state", "health_mental_state",
                                "key_projects",
                              pval=pval)
            sort_order = 5
            for kp in MentalHealthProjects.objects.filter(state__in=(AUS,state_num)):
                add_statistic_list_item(
                                "health_mental_state", "health_mental_state",
                                "key_projects",
                                kp.status_display(),
                                sort_order,
                                traffic_light_code = kp.status_tlc(),
                                label="(%s) %s" % (kp.state_display(), kp.project),
                                pval=pval
                )
                sort_order += 5
            messages.extend(
                    populate_raw_data(
                                "health_mental_state", "health_mental_state",
                                "mental_health", MentalHealthProjects, 
                                    {
                                        "project": "project",
                                        "progress": "progress_statement",
                                        "status_display": "status",
                                    },
                                use_dates=False,
                                pval=pval)
                    )
            messages.extend(
                    populate_raw_data(
                                "health_mental_state", "health_mental_state",
                                "data_table", MentalHealthProjects, 
                                    {
                                        "project": "project",
                                        "progress": "progress_statement",
                                        "status_display": "status",
                                    },
                                use_dates=False,
                                pval=pval)
                    )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

