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
from health_avoidable_deaths_uploader.models import *
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
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Age-standardised mortality rates of potentially avoidable deaths, under 75 years (per 100,000 persons)" or "Confidence Interval" or "RSE")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for rate, one for uncertainty, and one for RSE. May include optional National Benchmark row.'),
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
                                "Health", "Potentially Avoidable Deaths",
                                None, HealthAvoidableDeathsData,
                                {}, {
                                    "rate": "Age-standardised mortality rates of potentially avoidable deaths, under 75 years (per 100,000 persons)",
                                    "uncertainty": "Confidence Interval",
                                    "rse": "RSE",
                                },
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, None,
                                "avoidable-health-hero", "avoidable-health-hero",  
                                "avoidable-health-hero-state", "avoidable-health-hero-state",  
                                "health_avoidable", "health_avoidable",  
                                "health_avoidable_state", "health_avoidable_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "avoidable-health-hero-state", "avoidable-health-hero-state",  
                                "health_avoidable_state", "health_avoidable_state",
                                HealthAvoidableDeathsData, [ 
                                    ( "rate", "uncertainty", "rse"),
                                ],
                                want_increase=False,
                                verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "avoidable-health-hero", "avoidable-health-hero",  
                            "health-avoidable-hero-graph",
                            HealthAvoidableDeathsData, "rate",
                            [ AUS, ],
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "health_avoidable", "health_avoidable",  
                            "health_avoidable_summary_graph",
                            HealthAvoidableDeathsData, "rate",
                            [ AUS, ],
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "health_avoidable", "health_avoidable",  
                            "health_avoidable_detail_graph",
                            HealthAvoidableDeathsData, "rate",
                            use_error_bars=True,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data("health_avoidable", "health_avoidable",
                                "health_avoidable", HealthAvoidableDeathsData, 
                                {
                                    "rate": "rate_per_100k",
                                    "uncertainty": "uncertainty",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data("health_avoidable", "health_avoidable",
                                "data_table", HealthAvoidableDeathsData, 
                                {
                                    "rate": "rate",
                                    "uncertainty": "error",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                update_graph_data(
                                "avoidable-health-hero-state", "avoidable-health-hero-state",  
                                "health-avoidable-hero-graph",
                                HealthAvoidableDeathsData, "rate",
                                [ AUS, state_num ],
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                update_graph_data(
                                "health_avoidable_state", "health_avoidable_state",
                                "health_avoidable_summary_graph",
                                HealthAvoidableDeathsData, "rate",
                                [ AUS, state_num],
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "health_avoidable_state", "health_avoidable_state",
                                "health_avoidable_detail_graph",
                                HealthAvoidableDeathsData, "rate",
                                use_error_bars=True,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    populate_raw_data("health_avoidable_state", "health_avoidable_state",
                                "health_avoidable", HealthAvoidableDeathsData, 
                                {
                                    "rate": "rate_per_100k",
                                    "uncertainty": "uncertainty",
                                }, pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data("health_avoidable_state", "health_avoidable_state",
                                "data_table", HealthAvoidableDeathsData, 
                                {
                                    "rate": "rate",
                                    "uncertainty": "error",
                                }, pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

