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
from health_diabetes_uploader.models import *
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
                            ('B', 'Row Discriminator ("Proportion of persons aged 25 and over with type 2 diabetes (%)", "Confidence interval", "RSE")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for percentage, one for uncertainty and one for standard error'),
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
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
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
                                "Health", "Diabetes",
                                None, HealthDiabetesData,
                                {}, {
                                    "percentage": "Proportion of persons aged 25 and over with type 2 diabetes (%)", 
                                    "uncertainty": "Confidence interval",
                                    "rse": "RSE",
                                },
                                multi_year=True,
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "diabetes-health-hero", "diabetes-health-hero",  
                                "diabetes-health-hero-state", "diabetes-health-hero-state",  
                                "health_diabetes", "health_diabetes",  
                                "health_diabetes_state", "health_diabetes_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "diabetes-health-hero-state", "diabetes-health-hero-state",  
                                "health_diabetes_state", "health_diabetes_state",
                                HealthDiabetesData, [ 
                                    ( "percentage", "uncertainty", "rse" ),
                                ],
                                override_status="new_indicator",
                                verbosity=verbosity))
        latest_aust = HealthDiabetesData.objects.filter(state=AUS).order_by("year").last()
        set_statistic_data("diabetes-health-hero", "diabetes-health-hero",  
                        'benchmark', 5.0,
                        traffic_light_code="new_benchmark"
        )
        set_statistic_data("diabetes-health-hero", "diabetes-health-hero",  
                        'prevalence', 
                        latest_aust.percentage,
                        traffic_light_code="on_track",
                        label=latest_aust.year_display()
        )
        set_statistic_data("health_diabetes", "health_diabetes",  
                        'benchmark', 5.0,
                        traffic_light_code="new_benchmark"
        )
        set_statistic_data("health_diabetes", "health_diabetes",  
                        'prevalence', 
                        latest_aust.percentage,
                        traffic_light_code="on_track",
                        label=latest_aust.year_display()
        )
        messages.extend(
                update_my_graph_data("health_diabetes", "health_diabetes",  
                            "health_diabetes_detail_graph",
                            latest_aust.year,
                            verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data("health_diabetes", "health_diabetes",  
                                "health_diabetes", HealthDiabetesData,
                                {
                                    "percentage": "percentage_diabetes_prevalence",
                                    "uncertainty": "uncertainty",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data("health_diabetes", "health_diabetes",  
                                "data_table", HealthDiabetesData,
                                {
                                    "percentage": "prevalence",
                                    "uncertainty": "uncertainty",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            latest_state = HealthDiabetesData.objects.filter(state=state_num).order_by("year").last()
            set_statistic_data("diabetes-health-hero-state", "diabetes-health-hero-state",  
                            'benchmark', 5.0,
                            traffic_light_code="new_benchmark",
                            pval=pval
            )
            set_statistic_data("diabetes-health-hero-state", "diabetes-health-hero-state",  
                            'prevalence', 
                            latest_aust.percentage,
                            traffic_light_code="on_track",
                            label="National " + latest_aust.year_display(),
                            pval=pval
            )
            if latest_state.percentage > Decimal("5.0"):
                tlc = "not_met"
            else:
                tlc = "on_track"
            set_statistic_data("diabetes-health-hero-state", "diabetes-health-hero-state",  
                            'prevalence_state', 
                            latest_state.percentage,
                            traffic_light_code=tlc,
                            label=latest_state.state_display() + " " + latest_aust.year_display(),
                            pval=pval
            )
            set_statistic_data("health_diabetes_state", "health_diabetes_state",  
                            'benchmark', 5.0,
                            traffic_light_code="new_benchmark",
                            pval=pval
            )
            set_statistic_data("health_diabetes_state", "health_diabetes_state",  
                            'prevalence', 
                            latest_aust.percentage,
                            traffic_light_code="on_track",
                            label="National " + latest_aust.year_display(),
                            pval=pval
            )
            set_statistic_data("health_diabetes_state", "health_diabetes_state",  
                            'prevalence_state', 
                            latest_state.percentage,
                            traffic_light_code=tlc,
                            label=latest_state.state_display() + " " + latest_aust.year_display(),
                            pval=pval
            )
            messages.extend(
                    update_my_graph_data("health_diabetes_state", "health_diabetes_state",  
                                "health_diabetes_detail_graph",
                                latest_aust.year,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    populate_raw_data("health_diabetes_state", "health_diabetes_state",  
                                    "health_diabetes", HealthDiabetesData,
                                    {
                                        "percentage": "percentage_diabetes_prevalence",
                                        "uncertainty": "uncertainty",
                                    },
                                    pval=pval)
                    )
            messages.extend(
                    populate_crosstab_raw_data("health_diabetes_state", "health_diabetes_state",  
                                    "data_table", HealthDiabetesData,
                                    {
                                        "percentage": "prevalence",
                                        "uncertainty": "uncertainty",
                                    },
                                    pval=pval)
                    )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_graph_data(wurl, wlbl, graphlbl,
            year,
            jurisdictions = None,
            benchmark=5.0,
            verbosity=0,
            pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graphlbl)
    clear_graph_data(g, pval=pval)
    qry = HealthDiabetesData.objects.filter(year=year)
    if jurisdictions:
        qry = qry.filter(state__in=jurisdictions)
    for o in qry:
        gd = add_graph_data(g, o.state_display().lower(), o.percentage, cluster="diabetes_prevalence",
                                val_min = o.percentage - o.uncertainty,
                                val_max = o.percentage + o.uncertainty,
                                pval=pval)
    gd = add_graph_data(g, "benchmark", benchmark,
                cluster="diabetes_prevalence",
                pval=pval)
    if verbosity > 2:
        if pval:
            messages.append("Graph %s (%s) updated" % (graphlbl, pval.parameters()["state_abbrev"]))
        else:
            messages.append("Graph %s updated" % graphlbl)
    return messages

