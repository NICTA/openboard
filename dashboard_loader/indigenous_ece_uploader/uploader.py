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
from indigenous_ece_uploader.models import *
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
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Indigenous" or "Non-Indigenous")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pairs of rows per year, one for Indigenous, one for Non-Indigenous.'),
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
                                "Indigenous", "Early Childhood Education",
                                None, IndigenousECEData,
                                {}, {
                                    "indigenous": "Indigenous",
                                    "non_indigenous": "Non-Indigenous",
                                },
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "indig_ece-indigenous-hero", "indig_ece-indigenous-hero", 
                                "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                                "indigenous_indig_ece", "indigenous_indig_ece",
                                "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                                "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                                IndigenousECEData, 
                                [ ("indigenous", None),],
                                verbosity=verbosity))
        latest_aust = IndigenousECEData.objects.filter(state=AUS).order_by("year").last()
        set_statistic_data(
                        "indig_ece-indigenous-hero", "indig_ece-indigenous-hero", 
                        'non_indigenous',
                        latest_aust.non_indigenous,
                        traffic_light_code="new_benchmark")
        set_statistic_data(
                        "indig_ece-indigenous-hero", "indig_ece-indigenous-hero", 
                        'indigenous',
                        latest_aust.indigenous,
                        traffic_light_code=desc["status"]["tlc"])
        set_statistic_data(
                        "indigenous_indig_ece", "indigenous_indig_ece",
                        'non_indigenous',
                        latest_aust.non_indigenous,
                        traffic_light_code="new_benchmark")
        set_statistic_data(
                        "indigenous_indig_ece", "indigenous_indig_ece",
                        'indigenous',
                        latest_aust.indigenous,
                        traffic_light_code=desc["status"]["tlc"])
        messages.extend(
                update_my_graph_data(
                            "indigenous_indig_ece", "indigenous_indig_ece",
                            "indigenous_indig_ece_detail_graph",
                            latest_aust.year)
        )
        messages.extend(
                populate_raw_data(
                            "indigenous_indig_ece", "indigenous_indig_ece",
                            "indigenous_indig_ece", IndigenousECEData, 
                                {
                                    "indigenous": "indigenous",
                                    "non_indigenous": "non_indigenous",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data(
                            "indigenous_indig_ece", "indigenous_indig_ece",
                                "data_table", IndigenousECEData, 
                                {
                                    "indigenous": "indigenous",
                                    "non_indigenous": "non_indigenous",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            latest_state = IndigenousECEData.objects.filter(state=state_num).order_by("year").last()
            set_statistic_data(
                            "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                            'non_indigenous',
                            latest_aust.non_indigenous,
                            pval=pval)
            set_statistic_data(
                            "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                            'indigenous',
                            latest_aust.indigenous,
                            traffic_light_code=desc["status"]["tlc"],
                            pval=pval)
            set_statistic_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            'non_indigenous',
                            latest_aust.non_indigenous,
                            pval=pval)
            set_statistic_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            'indigenous',
                            latest_aust.indigenous,
                            traffic_light_code=desc["status"]["tlc"],
                            pval=pval)
 
            set_statistic_data(
                            "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                            'non_indigenous_state',
                            latest_state.non_indigenous,
                            pval=pval)
            set_statistic_data(
                            "indig_ece-indigenous-hero-state", "indig_ece-indigenous-hero-state", 
                            'indigenous_state',
                            latest_state.indigenous,
                            pval=pval)
            set_statistic_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            'non_indigenous_state',
                            latest_state.non_indigenous,
                            pval=pval)
            set_statistic_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            'indigenous_state',
                            latest_state.indigenous,
                            pval=pval)
            messages.extend(
                    update_my_graph_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            "indigenous_indig_ece_detail_graph",
                            latest_aust.year,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            "indigenous_indig_ece", IndigenousECEData, 
                            {
                                "indigenous": "indigenous",
                                "non_indigenous": "non_indigenous",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "indigenous_indig_ece_state", "indigenous_indig_ece_state",
                            "data_table", IndigenousECEData, 
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

def update_my_graph_data(wurl, wlbl, graph, latest_year, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    for i in IndigenousECEData.objects.all().filter(year=latest_year):
        add_graph_data(g, "indigenous", i.indigenous, 
                    cluster=i.state_display().lower(),pval=pval)
        add_graph_data(g, "non_indigenous", i.non_indigenous, 
                    cluster=i.state_display().lower(),pval=pval)
    return messages

