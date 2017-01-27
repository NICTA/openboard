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
from housing_remote_condition_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_state_stats, update_stats
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
                            ('A', 'Year range e.g. 2011-12 or 2011-13'),
                            ('B', 'Proportion of indigenous persons in remote areas (%)'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'One row per year'),
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
                                "Housing", "Remote Poor Condition",
                                None, HousingRemoteConditionData,
                                {}, {"percentage": "Proportion of indigenous households in remote areas (%)",},
                                multi_year=True,
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, None,
                                "remote_condition-housing-hero", "remote_condition-housing-hero",  
                                None, None,
                                "housing_remote_condition", "housing_remote_condition",  
                                None, None,
                                verbosity))
        qry = HousingRemoteConditionData.objects.filter(state=AUS).order_by("year")
        ref = qry.first()
        latest = qry.last()
        set_statistic_data("remote_condition-housing-hero", "remote_condition-housing-hero",  
                        'reference', ref.percentage,
                        label=ref.year_display()
        )
        set_statistic_data("remote_condition-housing-hero", "remote_condition-housing-hero",  
                        'latest', latest.percentage,
                        traffic_light_code=desc["status"]["tlc"],
                        label=latest.year_display()
        )
        set_statistic_data("housing_remote_condition", "housing_remote_condition",  
                        'reference', ref.percentage,
                        label=ref.year_display()
        )
        set_statistic_data("housing_remote_condition", "housing_remote_condition",  
                        'latest', latest.percentage,
                        traffic_light_code=desc["status"]["tlc"],
                        label=latest.year_display()
        )
        g = get_graph("housing_remote_condition", "housing_remote_condition",  
                    "housing_remote_condition_detail_graph", )
        clear_graph_data(g, clusters=True)
        sort_order = 5
        for datum in qry:
            cluster = add_graph_dyncluster(g, datum.year_display(), sort_order, datum.year_display())
            gd = add_graph_data(g, "condition", datum.percentage, cluster=cluster)
        messages.extend(
                populate_raw_data("housing_remote_condition", "housing_remote_condition",  
                                "housing_remote_condition", HousingRemoteConditionData,
                                {
                                    "percentage": "percentage_poor_condition",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data("housing_remote_condition", "housing_remote_condition",  
                                "data_table", HousingRemoteConditionData,
                                {
                                    "percentage": "proportion",
                                })
                )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

