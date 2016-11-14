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
from education_yr12_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats

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
                    'Contains Survey of Education and Work data',
                    'Data in this worksheet may be overridden by data in worksheet Data2',
                ],
            },
            {
                "name": "Data2",
                "cols": [ 
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator (Always %)'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'One Row per year, containing percentage attainment'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Contains Census data',
                    'Data in this worksheet take precedence over data in worksheet Data1'
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

benchmark = "Lift the Year 12 or equivalent or Certificate III attainment rate to 90% by 2020"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data1",
                                "Education", "Year 12/Cert 3 Attainment (SEW data)",
                                None, EducationYr12Cert3AttainmentData,
                                {}, {"percentage": "%", "uncertainty": "+",},
                                verbosity)
                )
        messages.extend(
                load_state_grid(wb, "Data2",
                                "Education", "Year 12/Cert 3 Attainment (Census data)",
                                None, EducationYr12Cert3AttainmentData,
                                {}, {"percentage": "%", },
                                verbosity,
                                fld_defaults={
                                    "uncertainty": 0.0,
                                })
                )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                                "yr12-education-hero", "yr12-education-hero", 
                                None, None, 
                                None, None,
                                None, None,
                                verbosity))
        messages.extend(
                update_graph_data(
                            "yr12-education-hero", "yr12-education-hero",
                            "education-yr12-hero-graph",
                            EducationYr12Cert3AttainmentData, "percentage",
                            [ AUS, ],
                            benchmark_start=2006,
                            benchmark_end=2020,
                            benchmark_gen=lambda init: 0.9,
                            use_error_bars=False,
                            verbosity=verbosity)
                )

    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

