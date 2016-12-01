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
from housing_remote_indigenous_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_crosstab_raw_data, populate_raw_data, update_stats
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
                            "indigenous_remote-housing-hero-state", "indigenous_remote-housing-hero-state", 
                            "housing_remote_indigenous", "housing_remote_indigenous", 
                            "housing_remote_indigenous_state", "housing_remote_indigenous_state", 
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
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(update_summary_graph_data(
                        "indigenous_remote-housing-hero-state", 
                        "indigenous_remote-housing-hero-state", 
                        "housing-rih-hero-graph",
                        pval=pval))
            messages.extend(update_summary_graph_data(
                        "housing_remote_indigenous_state", 
                        "housing_remote_indigenous_state", 
                        "housing_remote_indigenous_summary_graph", 
                        pval=pval))
            messages.extend(update_detail_state_graph_data(pval))
            messages.extend(
                    populate_raw_data("housing_remote_indigenous", "housing_remote_indigenous",
                                "housing_indigenous_remote", HousingRemoteIndigenousData,
                                {
                                    "new_houses": "new",
                                    "refurbishments": "refurbished",
                                }, pval=pval)
                    )
            messages.extend(
                    populate_crosstab_raw_data("housing_remote_indigenous", "housing_remote_indigenous",
                                "data_table", HousingRemoteIndigenousData,
                                {
                                    "new_houses": "new",
                                    "refurbishments": "refurbished",
                                }, pval=pval)
                    )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_summary_graph_data(wurl, wlbl, graph_lbl, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph_lbl)
    clear_graph_data(g, pval=pval)
    add_graph_data(g, "benchmark", 4200, cluster="new", pval=pval)
    add_graph_data(g, "benchmark", 4800, cluster="refurbished", pval=pval)
    data = HousingRemoteIndigenousData.objects.filter(state=AUS).order_by("year").last()
    add_graph_data(g, "year", data.new_houses, cluster="new", pval=pval)
    add_graph_data(g, "year", data.refurbishments, cluster="refurbished", pval=pval)
    yr = data.year_display()
    if pval:
        set_dataset_override(g, "year", "%s (Aust)" % data.year_display())
        state_abbrev = pval.parameters()["state_abbrev"]
        state_num = state_map[state_abbrev]
        data = HousingRemoteIndigenousData.objects.filter(state=state_num).order_by("year").last()
        if data is not None:
            add_graph_data(g, "year_state", data.new_houses, cluster="new", pval=pval)
            add_graph_data(g, "year_state", data.refurbishments, cluster="refurbished", pval=pval)
        set_dataset_override(g, "year_state", "%s (%s)" % (yr, state_abbrev))
    else:
        set_dataset_override(g, "year", yr)
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

def update_detail_state_graph_data(pval):
    messages = []
    state_abbrev = pval.parameters()["state_abbrev"]
    state_num = state_map[state_abbrev]
    g = get_graph("housing_remote_indigenous_state", "housing_remote_indigenous_state",
                        "housing_remote_indigenous_detail_graph")
    clear_graph_data(g, pval=pval)
    year = 0
    add_graph_data(g, "new", 4200, cluster="benchmark", pval=pval)
    add_graph_data(g, "refurbished", 4800, cluster="benchmark", pval=pval)
    for data in HousingRemoteIndigenousData.objects.filter(state__in=[AUS, state_num]).order_by("-year"):
        if year and year != data.year:
            break
        year = data.year
        if data.state == AUS:
            cluster = "australia"
        else:
            cluster = "state"
        add_graph_data(g, "new", data.new_houses, cluster=cluster, pval=pval)
        add_graph_data(g, "refurbished", data.refurbishments, cluster=cluster, pval=pval)
    return messages

