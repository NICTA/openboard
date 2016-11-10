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
from housing_homelessness_npa_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data_nostate, update_stats
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
                            ('B', 'Row Discriminator ("Accomodation need met", "Need for services met", "Clients experiencing family and domestic violence", "Young people presenting alone")'),
                            ('C', "May contain '%'"),
                            ('...', 'Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '4 rows per year, one for each of the four indicator measures'),
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
                            ('Influences', '"Influences" text of indicator status description. One paragraph per line (optional)'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

indicators = "Increase in the number of clients whose accomodation needs are met; and a decrease in the number of clients experiencing family or domestic violence, and in the rate of young people presenting alone."


def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Housing", "Remote Indigenous Housing",
                                None, HousingHomelessnessNpaData,
                                {}, {
                                    "accommodation_needs_met": "Accommodation need met", 
                                    "service_needs_met": "Need for services met",
                                    "clients_exp_violence": "Clients experiencing family and domestic violence",
                                    "young_presenting_alone": "Young people presenting alone",
                                },
                                verbosity)
        )
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicators,
                            None, None,
                            "housing_homelessness_npa", "housing_homelessness_npa",
                            verbosity))
        messages.extend(update_my_graph_data("housing_homelessness_npa", "housing_homelessness_npa",
                            "housing_homelessness_npa_summary_graph", include_all_years=False))
        messages.extend(update_my_graph_data("housing_homelessness_npa", "housing_homelessness_npa",
                            "housing_homelessness_npa_detail_graph"))
        messages.extend(populate_raw_data_nostate(
                "housing_homelessness_npa", "housing_homelessness_npa",
                "housing_homelessness_npa_data",
                HousingHomelessnessNpaData, {
                    "accommodation_needs_met": "accommodation",
                    "service_needs_met": "services",
                    "clients_exp_violence": "violence",
                    "young_presenting_alone": "alone",
                }))
        messages.extend(populate_raw_data_nostate(
                "housing_homelessness_npa", "housing_homelessness_npa",
                "data_table",
                HousingHomelessnessNpaData, {
                    "accommodation_needs_met": "accommodation",
                    "service_needs_met": "services",
                    "clients_exp_violence": "violence",
                    "young_presenting_alone": "alone",
                }))
    except LoaderException, e:
        raise e
#   except Exception, e:
#        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_graph_data(wurl, wlbl, graph_lbl, include_all_years=True):
    messages = []
    g = get_graph(wurl, wlbl, graph_lbl)
    clear_graph_data(g, clusters=True)
    clusters = {}
    distys = HousingHomelessnessNpaData.objects.filter(state=AUS).order_by('year', 'financial_year').distinct('year', 'financial_year')
    if not include_all_years:
        miny = distys.first().year_display()
        maxy = distys.last().year_display()
        clusters[miny] = add_graph_dyncluster(g, miny, 10, miny)
        clusters[maxy] = add_graph_dyncluster(g, maxy, 20, maxy)
    else:
        sort_order = 10
        for d in distys:
            disp = d.year_display()
            clusters[disp] = add_graph_dyncluster(g, disp, sort_order, disp) 
            sort_order += 10
    for dat in HousingHomelessnessNpaData.objects.filter(state=AUS).all():
        if dat.year_display() in clusters:
            cluster = clusters[dat.year_display()]
            add_graph_data(g, "accommodation", dat.accommodation_needs_met, cluster=cluster)
            add_graph_data(g, "services", dat.service_needs_met, cluster=cluster)
            add_graph_data(g, "violence", dat.clients_exp_violence, cluster=cluster)
            add_graph_data(g, "alone", dat.young_presenting_alone, cluster=cluster)
    return messages

