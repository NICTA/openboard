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
from skills_higher_qual_uploader.models import *
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
                            ('B', 'Row Discriminator ("Dip" or "Adv Dip")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for the number of diplomas (Dip) and one for the number of advanced diplomas (Adv Dip)'),
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

benchmark = "Double the number of higher level qualification completions (diploma and advanced diploma) nationally between 2009 and 2020"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Skills", "Higher Qualifications",
                                None, SkillsHigherQualificationsData,
                                {}, {"diplomas": "Dip", "adv_diplomas": "Adv Dip",},
                                verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                                "higher_qual-skills-hero", "higher_qual-skills-hero", 
                                "higher_qual-skills-hero-state", "higher_qual-skills-hero-state",
                                "skills_higher_qual", "skills_higher_qual",
                                "skills_higher_qual_state", "skills_higher_qual_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "higher_qual-skills-hero-state", "higher_qual-skills-hero-state",
                                "skills_higher_qual_state", "skills_higher_qual_state",
                                SkillsHigherQualificationsData, [("total", None),],
                                verbosity=verbosity))
        messages.extend(
                update_graph_data(
                            "higher_qual-skills-hero", "higher_qual-skills-hero",
                            "skills-higher_qual-hero-graph",
                            SkillsHigherQualificationsData, "total",
                            [ AUS, ],
                            benchmark_start=2009,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: Decimal(2) * init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "skills_higher_qual", "skills_higher_qual", 
                            "skills_higher_qual_summary_graph",
                            SkillsHigherQualificationsData, "total",
                            [ AUS, ],
                            benchmark_start=2009,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: Decimal(2) * init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "skills_higher_qual", "skills_higher_qual", 
                            "skills_higher_qual_detail_graph",
                            SkillsHigherQualificationsData, "total",
                            benchmark_start=2009,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: Decimal(2) * init,
                            use_error_bars=True,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data(
                                "skills_higher_qual", "skills_higher_qual", 
                                "skills_higher_qual", SkillsHigherQualificationsData, 
                                {
                                    "diplomas": "diploma",
                                    "adv_diplomas": "advanced_diploma",
                                    "total": "total",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data(
                                "skills_higher_qual", "skills_higher_qual", 
                                "data_table", SkillsHigherQualificationsData, 
                                {
                                    "diplomas": "diploma",
                                    "adv_diplomas": "adv_diploma",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                update_graph_data(
                        "higher_qual-skills-hero", "higher_qual-skills-hero",
                        "skills-higher_qual-hero-graph",
                        SkillsHigherQualificationsData, "total",
                        [ AUS, state_num ],
                        benchmark_start=2009,
                        benchmark_end=2020,
                        benchmark_gen=lambda init: Decimal(2) * init,
                        use_error_bars=False,
                        verbosity=verbosity,
                        pval=pval)
            )
            messages.extend(
                update_graph_data(
                        "skills_higher_qual", "skills_higher_qual", 
                        "skills_higher_qual_summary_graph",
                        SkillsHigherQualificationsData, "total",
                        [ AUS, state_num ],
                        benchmark_start=2009,
                        benchmark_end=2020,
                        benchmark_gen=lambda init: Decimal(2) * init,
                        use_error_bars=False,
                        verbosity=verbosity,
                        pval=pval)
            )
            messages.extend(
                update_graph_data(
                        "skills_higher_qual", "skills_higher_qual", 
                        "skills_higher_qual_detail_graph",
                        SkillsHigherQualificationsData, "total",
                        benchmark_start=2009,
                        benchmark_end=2020,
                        benchmark_gen=lambda init: Decimal(2) * init,
                        use_error_bars=True,
                        verbosity=verbosity,
                        pval=pval)
            )
            messages.extend(
                populate_raw_data(
                            "skills_higher_qual", "skills_higher_qual", 
                            "skills_higher_qual", SkillsHigherQualificationsData, 
                            {
                                "diplomas": "diploma",
                                "adv_diplomas": "advanced_diploma",
                                "total": "total",
                            }, pval=pval)
            )
            messages.extend(
                populate_crosstab_raw_data(
                            "skills_higher_qual", "skills_higher_qual", 
                            "data_table", SkillsHigherQualificationsData, 
                            {
                                "diplomas": "diploma",
                                "adv_diplomas": "adv_diploma",
                            }, pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

