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
from indigenous_child_mortality_uploader.models import *
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
                            ('B', 'Row Discriminator ("Indigenous rate", "Non-Indigenous rate", "Upper confidence level", "Lower confidence level", "Target Indigenous rate", "Projected non-Indigenous rate")'),
                            ('...', 'Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "Column Heading row"),
                            ('...', '4 or 5 rows per year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Contains combined NSW/Qld/WA/SA/NT ("Aust") data only',
                    'Some years may have both of "Indigenous rate" and "Target Indigenous rate" rows, but all years will have at least one of them',
                    'Some years will have both of "Non-Indigenous rate" and "Projected non-Indigenous rate" but all years will have at least one of them',
                ],
            },
            {
                "name": "State Data",
                "cols": [ 
                            ('A', 'Year Range e.g. 2011-15'),
                            ('B', 'Cohort ("Indigenous", "Non-Indigenous" or "Comparison")'),
                            ('C', 'Unit ("Rate per 100,000", "Number of deaths", "Rate ratio", "Rate difference"'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '6 rows per year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Contains data broken down by state for a single date range',
                    'Indigenous and Non-Indigenous cohorts have "Rate per 100,000" and "Number of deaths" units.',
                    'Comparison cohort has "Rate ratio" and "Rate difference" units.'
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
                                "Indigenous", "Child Mortality (Aust data)",
                                None, IndigenousChildMortalityNationalData,
                                {}, {
                                        "indigenous": "Indigenous rate", 
                                        "non_indigenous": "Non-Indigenous rate", 
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
        IndigenousChildMortalityStateData.objects.all().delete()
        messages.extend(
                load_state_grid(wb, "State Data",
                                "Indigenous", "Child Mortality (State data)",
                                None, IndigenousChildMortalityStateData,
                                {}, {
                                        "indigenous": ("Indigenous", "Rate per 100,000"), 
                                        "non_indigenous": ("Non-Indigenous", "Rate per 100,000"), 
                                        "indigenous_deaths": ("Indigenous", "Number of deaths"),
                                        "non_indigenous_deaths": ("Non-Indigenous", "Number of deaths"),
                                        "rate_ratio": ("Comparison", "Rate ratio"),
                                        "rate_diff": ("Comparison", "Rate difference"),
                                    },
                                verbosity=verbosity, multi_year=True)
                )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                            "child_mortality-indigenous-hero", "child_mortality-indigenous-hero", 
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous_child_mortality", "indigenous_child_mortality",
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            verbosity))
        messages.extend(update_state_stats(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            IndigenousChildMortalityStateData, [],
                            override_status="no_trend_data",
                            verbosity=verbosity))
        messages.extend(
                 update_my_national_graph(
                    "child_mortality-indigenous-hero", "child_mortality-indigenous-hero", 
                    "indigenous-child_mortality-hero-graph",
                    summary=True,
                    verbosity=verbosity)
        )
        messages.extend(
                 update_my_national_graph(
                    "indigenous_child_mortality", "indigenous_child_mortality",
                    "indigenous_child_mortality_summary_graph",
                    summary=True,
                    verbosity=verbosity)
        )
        messages.extend(
                 update_my_national_graph(
                    "indigenous_child_mortality", "indigenous_child_mortality",
                    "indigenous_child_mortality_detail_graph",
                    verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_child_mortality", "indigenous_child_mortality",
                        "indigenous_child_mortality", IndigenousChildMortalityNationalData, 
                        { 
                            "non_indigenous": "non_indigenous_rate",
                            "indigenous": "indigenous_rate",
                            "variability_lower": "indigenous_variability_lower",
                            "variability_upper": "indigenous_variability_upper",
                            "indigenous_target": "indigenous_target",
                            "non_indigenous_projected": "non_indigenous_projected",
                        },
                        use_states=False)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_child_mortality", "indigenous_child_mortality",
                        "data_table", IndigenousChildMortalityNationalData, 
                        { 
                            "non_indigenous": "non_indigenous_rate",
                            "indigenous": "indigenous_rate",
                            "indigenous_target": "indigenous_target",
                            "non_indigenous_projected": "non_indigenous_projected",
                        },
                        use_states=False)
        )
        messages.extend(
                populate_raw_data(
                        "indigenous_child_mortality", "indigenous_child_mortality",
                        "indigenous_child_mortality_state", IndigenousChildMortalityStateData, 
                        {
                            "non_indigenous": "non_indigenous_rate",
                            "non_indigenous_deaths": "non_indigenous_deaths",
                            "indigenous": "indigenous_rate",
                            "indigenous_deaths": "indigenous_deaths",
                            "rate_ratio": "rate_ratio",
                            "rate_diff": "rate_difference",
                        })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            i = IndigenousChildMortalityStateData.objects.get(state=AUS)
            set_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous", i.indigenous,
                            pval=pval)
            set_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "non_indigenous", i.non_indigenous,
                            pval=pval)
            set_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "indigenous", i.indigenous,
                            pval=pval)
            set_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "non_indigenous", i.non_indigenous,
                            pval=pval)
            try:
                i = IndigenousChildMortalityStateData.objects.get(state=state_num)
                set_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous_state", i.indigenous,
                            pval=pval)
                set_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "non_indigenous_state", i.non_indigenous,
                            pval=pval)
                set_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "indigenous_state", i.indigenous,
                            pval=pval)
                set_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "non_indigenous_state", i.non_indigenous,
                            pval=pval)
            except IndigenousChildMortalityStateData.DoesNotExist:
                clear_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous_state",
                            pval=pval)
                clear_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "non_indigenous_state",
                            pval=pval)
                clear_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "indigenous_state",
                            pval=pval)
                clear_statistic_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "non_indigenous_state",
                            pval=pval)
            messages.extend(
                    update_my_state_graph(pval, verbosity)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "indigenous_child_mortality", IndigenousChildMortalityNationalData, 
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
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "data_table", IndigenousChildMortalityStateData, 
                            { 
                                "non_indigenous": "non_indigenous_rate",
                                "non_indigenous_deaths": "non_indigenous_deaths",
                                "indigenous": "indigenous_rate",
                                "indigenous_deaths": "indigenous_deaths",
                                "rate_ratio": "rate_ratio",
                                "rate_diff": "rate_difference",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "indigenous_child_mortality_state", "indigenous_child_mortality_state",
                            "indigenous_child_mortality_state", IndigenousChildMortalityStateData, 
                            {
                                "non_indigenous": "non_indigenous_rate",
                                "non_indigenous_deaths": "non_indigenous_deaths",
                                "indigenous": "indigenous_rate",
                                "indigenous_deaths": "indigenous_deaths",
                                "rate_ratio": "rate_ratio",
                                "rate_diff": "rate_difference",
                            },
                            pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_national_graph(wurl, wlbl, graph, summary=False, verbosity=0):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g)
    for i in IndigenousChildMortalityNationalData.objects.order_by("year"):
        if i.indigenous:
            add_graph_data(g, "indigenous", i.indigenous, horiz_value=i.year_as_date())
        if i.non_indigenous:
            add_graph_data(g, "non_indigenous", i.non_indigenous, horiz_value=i.year_as_date())
        if i.indigenous_target:
            add_graph_data(g, "indigenous_target", i.indigenous_target, horiz_value=i.year_as_date())
        if i.non_indigenous_projected:
            add_graph_data(g, "non_indigenous_projected", i.non_indigenous_projected, horiz_value=i.year_as_date())
        if not summary:
            add_graph_data(g, "indigenous_variability_lower", i.variability_lower, horiz_value=i.year_as_date())
            add_graph_data(g, "indigenous_variability_upper", i.variability_upper, horiz_value=i.year_as_date())
    return messages

def update_my_state_graph(pval, verbosity):
    messages = []
    g = get_graph("indigenous_child_mortality_state", "indigenous_child_mortality_state",
                        "indigenous_child_mortality_detail_graph")
    clear_graph_data(g, pval=pval)
    for i in IndigenousChildMortalityStateData.objects.all():
        add_graph_data(g, "indigenous", i.indigenous, cluster=i.state_display().lower(), pval=pval)
        add_graph_data(g, "non_indigenous", i.non_indigenous, cluster=i.state_display().lower(), pval=pval)
    return messages
