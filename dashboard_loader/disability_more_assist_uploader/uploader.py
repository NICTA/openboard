#   Copyright 2016,2017 CSIRO
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
from disability_more_assist_uploader.models import *
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
                            ('B', 'Row Discriminator ("Proportion of people with disability aged 0-64 years who need more formal assistance than they are currently receiving (%)", "Confidence interval" or "RSE")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for each row discriminator value. May include a "National Benchmark" row which is not read'),
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
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                            ('(State abbrev)', 'Specific notes for individual states/territories'),
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
                                "Disability", "Need for More Assistance",
                                None, DisabilityMoreAssistData,
                                {}, {
                                    "percentage": "Proportion of people with disability aged 0-64 years who need more formal assistance than they are currently receiving (%)",
                                    "uncertainty": "Confidence interval",
                                    "rse": "RSE",
                                },
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "more_assist-disability-hero", "more_assist-disability-hero", 
                                "more_assist-disability-hero-state", "more_assist-disability-hero-state", 
                                "disability_more_assist", "disability_more_assist",
                                "disability_more_assist_state", "disability_more_assist_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "more_assist-disability-hero-state", "more_assist-disability-hero-state", 
                                "disability_more_assist_state", "disability_more_assist_state",
                                DisabilityMoreAssistData, 
                                [
                                    ("percentage", "uncertainty", "rse"),
                                ],
                                verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "more_assist-disability-hero", "more_assist-disability-hero", 
                            "disability-more_assist-hero-graph",
                            DisabilityMoreAssistData, "percentage",
                            [ AUS, ],
                            benchmark_start=2009,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: init-Decimal(5),
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "disability_more_assist", "disability_more_assist",
                            "disability_more_assist_summary_graph",
                            DisabilityMoreAssistData, "percentage",
                            [ AUS, ],
                            benchmark_start=2009,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: init-Decimal(5),
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "disability_more_assist", "disability_more_assist",
                            "disability_more_assist_detail_graph",
                            DisabilityMoreAssistData, "percentage",
                            benchmark_start=2009,
                            benchmark_end=2018,
                            benchmark_gen=lambda init: init-Decimal(5),
                            use_error_bars=True,
                            verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data(
                                "disability_more_assist", "disability_more_assist",
                                "disability_more_assist", DisabilityMoreAssistData,
                                {
                                    "percentage": "disabled_need_more_assist",
                                    "uncertainty": "uncertainty",
                                })
        )
        messages.extend(
                populate_crosstab_raw_data(
                                "disability_more_assist", "disability_more_assist",
                                "data_table", DisabilityMoreAssistData,
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
                                "more_assist-disability-hero-state", "more_assist-disability-hero-state", 
                                "disability-more_assist-hero-graph",
                                DisabilityMoreAssistData, "percentage",
                                [ AUS, state_num ],
                                benchmark_start=2009,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: init-Decimal(5),
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "disability_more_assist_state", "disability_more_assist_state",
                                "disability_more_assist_summary_graph",
                                DisabilityMoreAssistData, "percentage",
                                [ AUS, state_num ],
                                benchmark_start=2009,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: init-Decimal(5),
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "disability_more_assist_state", "disability_more_assist_state",
                                "disability_more_assist_detail_graph",
                                DisabilityMoreAssistData, "percentage",
                                benchmark_start=2009,
                                benchmark_end=2018,
                                benchmark_gen=lambda init: init-Decimal(5),
                                use_error_bars=True,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                                    "disability_more_assist_state", "disability_more_assist_state",
                                    "disability_more_assist", DisabilityMoreAssistData,
                                    {
                                        "percentage": "disabled_need_more_assist",
                                        "uncertainty": "uncertainty",
                                    },
                                    pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                                    "disability_more_assist_state", "disability_more_assist_state",
                                    "data_table", DisabilityMoreAssistData,
                                    {
                                        "percentage": "percent",
                                        "uncertainty": "error",
                                    },
                                    pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

