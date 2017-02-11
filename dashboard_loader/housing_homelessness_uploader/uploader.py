#   Copyright 2016,2017 Data61
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
from housing_homelessness_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_crosstab_raw_data, populate_raw_data, update_stats, update_state_stats
from django.template import Template, Context
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
                            ('B', 'Row Discriminator ("no.", % or "rate per 10k")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for number (no.), one for percentage of national total (%), and one for rate (rate per 10k)'),
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
                                "Housing", "Homelessness",
                                None, HousingHomelessData,
                                {}, {
                                    "homeless_persons": "no.", 
                                    "percent_of_national": "%",
                                    "rate_per_10k": "rate per 10k",
                                },
                                verbosity=verbosity)
                )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                            "homelessness-housing-hero", "homelessness-housing-hero", 
                            "homelessness-housing-hero-state", "homelessness-housing-hero-state", 
                            "housing_homelessness", "housing_homelessness", 
                            "housing_homelessness_state", "housing_homelessness_state", 
                            verbosity))
        messages.extend(update_state_stats(
                            "homelessness-housing-hero-state", "homelessness-housing-hero-state", 
                            "housing_homelessness_state", "housing_homelessness_state", 
                            HousingHomelessData, [ ("rate_per_10k", None,), ],
                            want_increase=False,
                            verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "homelessness-housing-hero", "homelessness-housing-hero",
                            "housing-hln-hero-graph",
                            HousingHomelessData, "homeless_persons",
                            [ AUS, ],
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: Decimal(0.93)*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        p =  Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                update_graph_data(
                            "homelessness-housing-hero-state", "homelessness-housing-hero-state",
                            "housing-hln-hero-graph",
                            HousingHomelessData, "homeless_persons",
                            [ AUS, state_num ],
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: Decimal(0.93) * init,
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
        messages.extend(
                update_graph_data(
                            "housing_homelessness", "housing_homelessness",
                            "housing_homelessness_summary_graph",
                            HousingHomelessData, "homeless_persons",
                            [ AUS, ],
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: Decimal(0.93)*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "housing_homelessness", "housing_homelessness",
                            "housing_homelessness_detail_graph",
                            HousingHomelessData, "homeless_persons",
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: Decimal(0.93)*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data("housing_homelessness", "housing_homelessness",
                            "housing_homelessness", HousingHomelessData,
                            {
                                "homeless_persons": "number_homeless_persons",
                                "percent_of_national": "proportion_national_total",
                                "rate_per_10k": "rate_per_10k",
                            })
                )
        messages.extend(
                populate_crosstab_raw_data("housing_homelessness", "housing_homelessness",
                            "data_table", HousingHomelessData,
                            {
                                "homeless_persons": "persons",
                                "percent_of_national": "proportion",
                                "rate_per_10k": "rate10k",
                            })
                )
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                    update_graph_data(
                                "housing_homelessness_state", "housing_homelessness_state",
                                "housing_homelessness_summary_graph",
                                HousingHomelessData, "homeless_persons",
                                [ AUS, state_num ],
                                benchmark_start=2006,
                                benchmark_end=2013,
                                benchmark_gen=lambda init: Decimal(0.93)*init,
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
                    )
            messages.extend(
                    update_graph_data(
                                "housing_homelessness_state", "housing_homelessness_state",
                                "housing_homelessness_detail_graph",
                                HousingHomelessData, "homeless_persons",
                                benchmark_start=2006,
                                benchmark_end=2013,
                                benchmark_gen=lambda init: Decimal(0.93)*init,
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
                    )
            messages.extend(
                    populate_raw_data("housing_homelessness_state", "housing_homelessness_state",
                                "housing_homelessness", HousingHomelessData,
                                {
                                    "homeless_persons": "number_homeless_persons",
                                    "percent_of_national": "proportion_national_total",
                                    "rate_per_10k": "rate_per_10k",
                                },
                                pval=pval)
                    )
            messages.extend(
                    populate_crosstab_raw_data("housing_homelessness_state", "housing_homelessness_state",
                                "data_table", HousingHomelessData,
                                {
                                    "homeless_persons": "persons",
                                    "percent_of_national": "proportion",
                                    "rate_per_10k": "rate10k",
                                },
                                pval=pval)
                    )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

