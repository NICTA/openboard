#   Copyright 2016 CSIRO
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
from infrastructure_npa_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats
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
                "name": "Data1",
                "cols": [ 
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Complete", "Underway", or "Pending")'),
                            ('...', 'Column per state'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows of project counts per year, one each for complete, pending and underway'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'No national (Aust) column',
                ],
            },
            {
                "name": "Data2",
                "cols": [ 
                            ('A', 'Year e.g. 2007-14 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Complete", "Underway", or "Pending")'),
                            ('...', 'Column per state'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows of percentage of funds per year, one each for complete, pending and underway'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Data3",
                "cols": [ 
                            ('A', 'State'),
                            ('B', 'Key Project")'),
                            ('C', 'Project Milestones'),
                            ('D', 'Project Status'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "Column Heading row"),
                            ('...', 'Row per key project'),
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
                            ('Status', 'Benchmark status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of benchmark status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line (optional)'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

benchmark = "Deliver major land transport infrastructure projects on schedule"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data1",
                                "Infrastructure", "Projects (Counts)",
                                None, InfrastructureProjectCounts,
                                {}, {
                                        "completed": "Completed",
                                        "underway": "Underway",
                                        "pending": "Pending",
                                    },
                                verbosity)
                )
        messages.extend(
                load_state_grid(wb, "Data2",
                                "Infrastructure", "Projects (Proportion of funds)",
                                None, InfrastructureProjectFundingProportion,
                                {}, {
                                        "completed": "Completed",
                                        "underway": "Underway",
                                        "pending": "Pending",
                                    },
                                verbosity)
                )
        # TODO Read in tab3.
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                            "projects-infrastructure-hero", "projects-infrastructure-hero", 
                            "projects-infrastructure-hero-state", "projects-infrastructure-hero-state", 
                            None, None,
                            None, None,
                            verbosity))
        messages.extend(update_state_stats(
                            "projects-infrastructure-hero-state", "projects-infrastructure-hero-state", 
                            None, None,
                            None, None, None,
                            override_status="improving",
                            verbosity=verbosity))
        aust_sums = InfrastructureProjectCounts.objects.aggregate(Sum('completed'), Sum('underway'), Sum('pending'))
        set_statistic_data("projects-infrastructure-hero", "projects-infrastructure-hero",
                            "pending", float(aust_sums["pending__sum"]),
                            traffic_light_code=desc["status"]["tlc"])
        set_statistic_data("projects-infrastructure-hero", "projects-infrastructure-hero",
                            "completed", float(aust_sums["completed__sum"]),
                            traffic_light_code=desc["status"]["tlc"])
        set_statistic_data("projects-infrastructure-hero", "projects-infrastructure-hero",
                            "underway", float(aust_sums["underway__sum"]),
                            traffic_light_code=desc["status"]["tlc"])
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_counts = InfrastructureProjectCounts.objects.get(state=state_num)
            set_statistic_data(
                        "projects-infrastructure-hero-state", "projects-infrastructure-hero-state",
                        "completed", float(aust_sums["completed__sum"]),
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "projects-infrastructure-hero-state", "projects-infrastructure-hero-state",
                        "underway", float(aust_sums["underway__sum"]),
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "projects-infrastructure-hero-state", "projects-infrastructure-hero-state",
                        "completed_state", float(state_counts.completed),
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
            set_statistic_data(
                        "projects-infrastructure-hero-state", "projects-infrastructure-hero-state",
                        "underway_state", float(state_counts.underway),
                        traffic_light_code=desc["status"]["tlc"],
                        pval=pval)
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages


