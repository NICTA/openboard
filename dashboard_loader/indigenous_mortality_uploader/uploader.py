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
from indigenous_mortality_uploader.models import *
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
                "name": "Data",
                "cols": [ 
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Indigenous mortality rate", "Non-Indigenous mortality rate", "Upper confidence level", "Lower confidence level", "Target Indigenous rate", "Projected non-Indigenous rate")'),
                            ('...', 'Columns for included states (NSW, Qld, SA, NT) and Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "Column Heading row"),
                            ('...', '4 or 5 rows per year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    '"Aust" column contains combined NSW/Qld/SA/NT data',
                    'Some years may have both of "Indigenous rate" and "Target Indigenous rate" rows, but all years will have at least one of them',
                    'Some years will have both of "Non-Indigenous rate" and "Projected non-Indigenous rate" but all years will have at least one of them',
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
                                "Indigenous", "Mortality",
                                None, IndigenousMortalityData,
                                {}, {
                                        "indigenous": "Indigenous mortality rate", 
                                        "non_indigenous": "Non-Indigenous mortality rate", 
                                        "variability_lower": "Lower confidence level",
                                        "variability_upper": "Upper confidence level",
                                        "indigenous_target": "Target Indigenous rate",
                                        "non_indigenous_projected": "Projected non-Indigenous rate"
                                    },
                                optional_rows=[
                                        "indigenous",
                                        "non_indigenous",
                                        "indigenous_target",
                                        "non_indigenous_projected",
                                ],
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                            "indig_mortality-indigenous-hero", "indig_mortality-indigenous-hero", 
                            "indig_mortality-indigenous-hero-state", "indig_mortality-indigenous-hero-state", 
                            "indigenous_indig_mortality", "indigenous_indig_mortality",
                            "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                            verbosity))
        messages.extend(update_state_stats(
                            "indig_mortality-indigenous-hero-state", "indig_mortality-indigenous-hero-state", 
                            "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                            IndigenousMortalityData, [],
                            query_filter_kwargs={ "indigenous__isnull": False },
                            restrict_states = [ NSW, QLD, SA, NT ],
                            use_benchmark_tls=True,
                            status_func=IndigenousMortalityData.tlc,
                            verbosity=verbosity))
        messages.extend(
                 update_my_graph(
                    "indig_mortality-indigenous-hero", "indig_mortality-indigenous-hero", 
                    "indigenous-indig_mortality-hero-graph",
                    summary=True,
                    verbosity=verbosity)
        )
        messages.extend(
                 update_my_graph(
                    "indigenous_indig_mortality", "indigenous_indig_mortality",
                    "indigenous_indig_mortality_summary_graph",
                    summary=True,
                    verbosity=verbosity)
        )
        messages.extend(
                 update_my_graph(
                    "indigenous_indig_mortality", "indigenous_indig_mortality",
                    "indigenous_indig_mortality_detail_graph",
                    verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_indig_mortality", "indigenous_indig_mortality",
                        "indigenous_indig_mortality", IndigenousMortalityData, 
                        { 
                            "non_indigenous": "non_indigenous_rate",
                            "indigenous": "indigenous_rate",
                            "variability_lower": "indigenous_variability_lower",
                            "variability_upper": "indigenous_variability_upper",
                            "indigenous_target": "indigenous_target",
                            "non_indigenous_projected": "non_indigenous_projected",
                        }
                )
        )
        messages.extend(
                populate_crosstab_raw_data(
                        "indigenous_indig_mortality", "indigenous_indig_mortality",
                        "data_table", IndigenousMortalityData, 
                        { 
                            "non_indigenous_csv_display": "non_indigenous_rate",
                            "indigenous": "indigenous_rate",
                        },
                        query_kwargs = {
                            "indigenous__isnull": False,
                        }
                )
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            if state_num not in [ NSW, SA, NT, QLD ]:
                continue
            messages.extend(
                     update_my_graph(
                        "indig_mortality-indigenous-hero-state", "indig_mortality-indigenous-hero-state", 
                        "indigenous-indig_mortality-hero-summary_graph",
                        summary=True,
                        verbosity=verbosity,
                        state_num=state_num,
                        pval=pval)
            )
            messages.extend(
                     update_my_graph(
                        "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                        "indigenous_indig_mortality_summary_graph",
                        summary=True,
                        verbosity=verbosity,
                        state_num=state_num,
                        pval=pval)
            )
            messages.extend(
                     update_my_graph(
                        "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                        "indigenous_indig_mortality_detail_graph",
                        verbosity=verbosity,
                        state_num=state_num,
                        pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                            "indigenous_indig_mortality", IndigenousMortalityData, 
                            { 
                                "non_indigenous": "non_indigenous_rate",
                                "indigenous": "indigenous_rate",
                                "variability_lower": "indigenous_variability_lower",
                                "variability_upper": "indigenous_variability_upper",
                                "indigenous_target": "indigenous_target",
                                "non_indigenous_projected": "non_indigenous_projected",
                            },
                            use_states=False,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                            "indigenous_indig_mortality", IndigenousMortalityData, 
                            { 
                                "non_indigenous": "non_indigenous_rate",
                                "indigenous": "indigenous_rate",
                                "variability_lower": "indigenous_variability_lower",
                                "variability_upper": "indigenous_variability_upper",
                                "indigenous_target": "indigenous_target",
                                "non_indigenous_projected": "non_indigenous_projected",
                            },
                            pval=pval
                    )
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "indigenous_indig_mortality_state", "indigenous_indig_mortality_state",
                            "data_table", IndigenousMortalityData, 
                            { 
                                "non_indigenous_csv_display": "non_indigenous_rate",
                                "indigenous": "indigenous_rate",
                            },
                            query_kwargs = {
                                "indigenous__isnull": False,
                            },
                            pval=pval
                    )
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_graph(wurl, wlbl, graph, summary=False, pval=None, state_num=AUS,verbosity=0):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    for i in IndigenousMortalityData.objects.filter(state=state_num).order_by("year"):
        if i.indigenous:
            add_graph_data(g, "indigenous", i.indigenous, horiz_value=i.year_as_date(), pval=pval)
        if i.non_indigenous:
            add_graph_data(g, "non_indigenous", i.non_indigenous, horiz_value=i.year_as_date(), pval=pval)
        if not summary:
            add_graph_data(g, "indigenous_variability_lower", i.variability_lower, horiz_value=i.year_as_date(), pval=pval)
            add_graph_data(g, "indigenous_variability_upper", i.variability_upper, horiz_value=i.year_as_date(), pval=pval)
            if i.indigenous_target:
                add_graph_data(g, "indigenous_target", i.indigenous_target, horiz_value=i.year_as_date(), pval=pval)
            if i.non_indigenous_projected:
                add_graph_data(g, "non_indigenous_projected", i.non_indigenous_projected, horiz_value=i.year_as_date(), pval=pval)
    return messages

