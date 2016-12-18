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
from skills_improved_employment_uploader.models import *
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
                            ('B', 'Row Discriminator (% or +)'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for percentage (%) and one for uncertainty (+)'),
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
                            ('Status', 'Indicator status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of indicator status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of indicator status description. One paragraph per line'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

indicator = "Increase the proportion of VET graduates with improved employment status after training"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Skills", "Improved Employment Status",
                                None, SkillsImprovedEmployData,
                                {}, {"percentage": "%", "uncertainty": "+",},
                                verbosity,
                                transforms={ "percentage": lambda x: 100.0-x, }))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicator,
                                "improved_employ-skills-hero", "improved_employ-skills-hero", 
                                "improved_employ-skills-hero-state", "improved_employ-skills-hero-state",
                                "skills_improved_employ", "skills_improved_employ",
                                "skills_improved_employ_state", "skills_improved_employ_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "improved_employ-skills-hero-state", "improved_employ-skills-hero-state",
                                "skills_improved_employ_state", "skills_improved_employ_state",
                                SkillsImprovedEmployData, [("percentage", "uncertainty",),],
                                want_increase=False,
                                verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "improved_employ-skills-hero", "improved_employ-skills-hero",
                            "skills-improved_employ-hero-graph",
                            SkillsImprovedEmployData, "percentage",
                            [ AUS, ],
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "skills_improved_employ", "skills_improved_employ", 
                            "skills_improved_employ_summary_graph",
                            SkillsImprovedEmployData, "percentage",
                            [ AUS, ],
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "skills_improved_employ", "skills_improved_employ", 
                            "skills_improved_employ_detail_graph",
                            SkillsImprovedEmployData, "percentage",
                            use_error_bars=True,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data(
                                "skills_improved_employ", "skills_improved_employ", 
                                "skills_improved_employ", SkillsImprovedEmployData,
                                {
                                    "percentage": "percentage_improved_employment",
                                    "uncertainty": "uncertainty",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data(
                                "skills_improved_employ", "skills_improved_employ", 
                                "data_table", SkillsImprovedEmployData,
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
                            "improved_employ-skills-hero-state", "improved_employ-skills-hero-state",
                            "skills-improved_employ-hero-graph",
                            SkillsImprovedEmployData, "percentage",
                            [ AUS, state_num ],
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
            messages.extend(
                    update_graph_data(
                            "skills_improved_employ_state", "skills_improved_employ_state", 
                            "skills_improved_employ_summary_graph",
                            SkillsImprovedEmployData, "percentage",
                            [ AUS, state_num ],
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
            messages.extend(
                    update_graph_data(
                            "skills_improved_employ_state", "skills_improved_employ_state", 
                            "skills_improved_employ_detail_graph",
                            SkillsImprovedEmployData, "percentage",
                            use_error_bars=True,
                            verbosity=verbosity,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                            "skills_improved_employ_state", "skills_improved_employ_state", 
                            "skills_improved_employ", SkillsImprovedEmployData,
                            {
                                "percentage": "percentage_improved_employment",
                                "uncertainty": "uncertainty",
                            }, pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data(
                            "skills_improved_employ_state", "skills_improved_employ_state", 
                            "data_table", SkillsImprovedEmployData,
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

