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
from health_smoking_uploader.models import *
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
                            ('B', 'Row Discriminator ("Proportion of adults who are current daily smokers (%)", "Confidence Interval", or "RSE")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for percentage, one for uncertainty, and one for RSE. May include optional National Benchmark row.'),
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
                                "Health", "Smoking Rate",
                                None, HealthSmokingData,
                                {}, {
                                    "percentage": "Proportion of adults who are current daily smokers (%)", 
                                    "uncertainty": "Confidence Interval",
                                    "rse": "RSE",
                                },
                                verbosity=verbosity,
                                multi_year=True)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "smoking-health-hero", "smoking-health-hero",  
                                "smoking-health-hero-state", "smoking-health-hero-state",  
                                "health_smoking", "health_smoking",  
                                "health_smoking_state", "health_smoking_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "smoking-health-hero-state", "smoking-health-hero-state",  
                                "health_smoking_state", "health_smoking_state",
                                HealthSmokingData, [ 
                                    ( "percentage", "uncertainty", "rse" ),
                                ],
                                want_increase=False,
                                verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "smoking-health-hero", "smoking-health-hero",  
                            "health-smoking-hero-graph",
                            HealthSmokingData, "percentage",
                            [ AUS, ],
                            benchmark_start=2008,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: Decimal(10),
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "health_smoking", "health_smoking",  
                            "health_smoking_summary_graph",
                            HealthSmokingData, "percentage",
                            [ AUS, ],
                            benchmark_start=2008,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: Decimal(10),
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "health_smoking", "health_smoking",  
                            "health_smoking_detail_graph",
                            HealthSmokingData, "percentage",
                            benchmark_start=2008,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: Decimal(10),
                            use_error_bars=True,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data("health_smoking", "health_smoking",
                                "health_smoking", HealthSmokingData, 
                                {
                                    "percentage": "percentage_smokers",
                                    "uncertainty": "uncertainty",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data("health_smoking", "health_smoking",
                                "data_table", HealthSmokingData, 
                                {
                                    "percentage": "percent",
                                    "uncertainty": "error",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                update_graph_data(
                                "smoking-health-hero-state", "smoking-health-hero-state",  
                                "health-smoking-hero-graph",
                                HealthSmokingData, "percentage",
                                [ AUS, state_num ],
                                benchmark_start=2008,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: Decimal(10),
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                update_graph_data(
                                "health_smoking_state", "health_smoking_state",
                                "health_smoking_summary_graph",
                                HealthSmokingData, "percentage",
                                [ AUS, state_num],
                                benchmark_start=2008,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: Decimal(10),
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "health_smoking_state", "health_smoking_state",
                                "health_smoking_detail_graph",
                                HealthSmokingData, "percentage",
                                benchmark_start=2008,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: Decimal(10),
                                use_error_bars=True,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    populate_raw_data("health_smoking", "health_smoking",
                                "health_smoking", HealthSmokingData, 
                                {
                                    "percentage": "percentage_smokers",
                                    "uncertainty": "uncertainty",
                                }, pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data("health_smoking", "health_smoking",
                                "data_table", HealthSmokingData, 
                                {
                                    "percentage": "percent",
                                    "uncertainty": "error",
                                }, pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

