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
                "name": "Data1",
                "cols": [ 
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Indigenous deaths per 100,000" or Non-Indigenous deaths per 100,000")'),
                            ('...', 'Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for indigenous, one for non-indigenous'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Contains combined NSW/Qld/WA/SA/NT ("Aust") data only',
                ],
            },
            {
                "name": "Data2",
                "cols": [ 
                            ('A', 'Year e.g. 2007-14 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Indigenous deaths per 100,000" or Non-Indigenous deaths per 100,000")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for indigenous, one for non-indigenous'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Contains data broken down by state for a single date range'
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

benchmark = "Halve the gap in mortality rates for Indigenous children under five within a decade (by 2018)"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data1",
                                "Indigenous", "Child Mortality (Aust data)",
                                None, IndigenousChildMortalityNationalData,
                                {}, {
                                        "indigenous": "Indigenous deaths per 100,000", 
                                        "non_indigenous": "Non-Indigenous deaths per 100,000", 
                                    },
                                verbosity)
                )
        messages.extend(
                load_state_grid(wb, "Data2",
                                "Indigenous", "Child Mortality (State data)",
                                None, IndigenousChildMortalityStateData,
                                {}, {
                                        "indigenous": "Indigenous deaths per 100,000", 
                                        "non_indigenous": "Non-Indigenous deaths per 100,000", 
                                    },
                                verbosity, multi_year=True)
                )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                            "child_mortality-indigenous-hero", "child_mortality-indigenous-hero", 
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            None, None,
                            None, None,
                            verbosity))
        messages.extend(update_state_stats(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            None, None,
                            IndigenousChildMortalityStateData, "gap", None,
                            want_increase=False,
                            verbosity=verbosity))
        messages.extend(
                 update_my_hero_graph(verbosity=verbosity)
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
            except IndigenousChildMortalityStateData.DoesNotExist:
                clear_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "indigenous_state",
                            pval=pval)
                clear_statistic_data(
                            "child_mortality-indigenous-hero-state", "child_mortality-indigenous-hero-state", 
                            "non_indigenous_state",
                            pval=pval)
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_hero_graph(verbosity):
    messages = []
    g = get_graph("child_mortality-indigenous-hero", "child_mortality-indigenous-hero", 
                            "indigenous-child_mortality-hero-graph")
    clear_graph_data(g)
    for i in IndigenousChildMortalityNationalData.objects.order_by("year"):
        add_graph_data(g, "indigenous", i.indigenous, horiz_value=i.year_as_date())
        add_graph_data(g, "non_indigenous", i.non_indigenous, horiz_value=i.year_as_date())
    return messages

