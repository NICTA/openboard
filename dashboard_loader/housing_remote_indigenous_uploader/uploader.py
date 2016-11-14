#   Copyright 2016 Data61
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
from housing_remote_indigenous_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_crosstab_raw_data, populate_raw_data, update_stats
from django.template import Template, Context

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
                            ('...', 'Pairs of rows per year, one for new homes (New), one for refurbishments (Refurbishments)'),
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
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line (optional)'),
                            ('Other Benchmarks', '(optional) Description and results or other benchmark(s) under the national partnership agreement that do not have their own widget(s).'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

benchmark = "From 2008, 4200 new houses to be delivered by 2018; and 4800 refurbishments to be delivered by 2014"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Housing", "Remote Indigenous Housing",
                                None, HousingRemoteIndigenousData,
                                {}, {
                                    "new_houses": "New", 
                                    "refurbishments": "Refurbishments",
                                },
                                verbosity)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                            "indigenous_remote-housing-hero", "indigenous_remote-housing-hero", 
                            None, None,
                            "housing_remote_indigenous", "housing_remote_indigenous", 
                            None, None,
                            verbosity))
        messages.extend(update_summary_graph_data(
                    "indigenous_remote-housing-hero", 
                    "indigenous_remote-housing-hero", 
                    "housing-rih-hero-graph"))
        messages.extend(update_summary_graph_data(
                    "housing_remote_indigenous", 
                    "housing_remote_indigenous", 
                    "housing_remote_indigenous_summary_graph"))
        messages.extend(update_detail_graph_data())
        messages.extend(
                populate_raw_data("housing_remote_indigenous", "housing_remote_indigenous",
                            "housing_indigenous_remote", HousingRemoteIndigenousData,
                            {
                                "new_houses": "new",
                                "refurbishments": "refurbished",
                            })
                )
        messages.extend(
                populate_crosstab_raw_data("housing_remote_indigenous", "housing_remote_indigenous",
                            "data_table", HousingRemoteIndigenousData,
                            {
                                "new_houses": "new",
                                "refurbishments": "refurbished",
                            })
                )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_summary_graph_data(wurl, wlbl, graph_lbl):
    messages = []
    g = get_graph(wurl, wlbl, graph_lbl)
    clear_graph_data(g)
    add_graph_data(g, "benchmark", 4200, cluster="new")
    add_graph_data(g, "benchmark", 4800, cluster="refurbished")
    data = HousingRemoteIndigenousData.objects.filter(state=AUS).order_by("year").last()
    add_graph_data(g, "year", data.new_houses, cluster="new")
    add_graph_data(g, "year", data.refurbishments, cluster="refurbished")
    set_dataset_override(g, "year", data.year_display())
    return messages

def update_detail_graph_data():
    messages = []
    g = get_graph("housing_remote_indigenous", "housing_remote_indigenous",
                        "housing_remote_indigenous_detail_graph")
    clear_graph_data(g)
    year = 0
    for data in HousingRemoteIndigenousData.objects.exclude(state=AUS).order_by("-year"):
        if year and year != data.year:
            break
        year = data.year
        add_graph_data(g, "new", data.new_houses, cluster=data.state_display().lower())
        add_graph_data(g, "refurbished", data.refurbishments, cluster=data.state_display().lower())
    return messages

