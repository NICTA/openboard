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
from skills_cert3_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats
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

benchmark = "Halve the proportion of Australians nationally aged 20-64 without qualifications at Certificate III level and above between 2009 and 2020"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Skills", "Certificate 3",
                                None, SkillsCert3Data,
                                {}, {"percentage": "%", "uncertainty": "+",},
                                verbosity,
                                transforms={ "percentage": lambda x: 100.0-x, }))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                                "cert3-skills-hero", "cert3-skills-hero", 
                                "cert3-skills-hero-state", "cert3-skills-hero-state",
                                None, None, None, None,
                                verbosity))
        messages.extend(
                update_graph_data(
                            "cert3-skills-hero", "cert3-skills-hero",
                            "skills-cert3-hero-graph",
                            SkillsCert3Data, "percentage",
                            [ AUS, ],
                            benchmark_start=2009,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: Decimal(0.5) * init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                update_graph_data(
                            "cert3-skills-hero-state", "cert3-skills-hero-state",
                            "skills-cert3-hero-graph",
                            SkillsCert3Data, "percentage",
                            [ AUS, state_num ],
                            benchmark_start=2009,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: Decimal(0.5) * init,
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

