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
from housing_homelessness_npa_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats
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

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Housing", "Homelessness NPA",
                                None, HousingHomelessnessNpaData,
                                {}, {
                                    "accommodation_needs_met": "Accommodation need met", 
                                    "service_needs_met": "Need for services met",
                                    "clients_exp_violence": "Clients experiencing family and domestic violence",
                                    "young_presenting_alone": "Young people presenting alone",
                                },
                                verbosity=verbosity)
        )
        messages.extend(
                load_state_grid(wb, "Progress",
                        "Housing", "Homelessness NPA Progress",
                        None, HousingHomelessnessNpaProgress,
                        {}, {
                            "plan1": "Part 1 of project plans submitted to the Commonwealth (1 July 2015)",
                            "plan2": "Part 2 of project plans submitted to the Commonwealth (1 September 2015)",
                            "update": "Update Commonwealth on assessment of progress against project plans, and provide assurance funding has been matched (1 September 2016)",
                            "matched_funding": "At least 25 per cent of total matched funding directed to addressing priority outputs",
                        },
                        verbosity=verbosity,
                        use_dates=False,
                        transforms = {
                            "plan1": lambda x: progress_map[x.strip()],
                            "plan2": lambda x: progress_map[x.strip()],
                            "update": lambda x: progress_map[x.strip()],
                            "matched_funding": lambda x: progress_map[x.strip()],
                        })
        )
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, None,
                            "homelessness_npa-housing-hero", "homelessness_npa-housing-hero", 
                            "homelessness_npa-housing-hero-state", "homelessness_npa-housing-hero-state", 
                            "housing_homelessness_npa", "housing_homelessness_npa", 
                            "housing_homelessness_npa_state", "housing_homelessness_npa_state", 
                            verbosity))
        messages.extend(update_state_stats(
                            "homelessness_npa-housing-hero-state", "homelessness_npa-housing-hero-state", 
                            "housing_homelessness_npa_state", "housing_homelessness_npa_state", 
                            HousingHomelessnessNpaData, [ ("accommodation_needs_met", None,), ],
                            verbosity=verbosity))
        messages.extend(update_progress("housing_homelessness_npa", "housing_homelessness_npa", verbosity=verbosity))
        messages.extend(update_mygraph_data("housing_homelessness_npa", "housing_homelessness_npa",
                            "housing_homelessness_npa_summary_graph", 
                            include_accom = True, include_services=True,
                            include_all_years=False))
        messages.extend(update_mygraph_data("homelessness_npa-housing-hero", "homelessness_npa-housing-hero",
                            "housing-hln_npa-hero-graph", 
                            include_accom = True, include_services=True,
                            include_all_years=False))
        messages.extend(update_mygraph_data("housing_homelessness_npa", "housing_homelessness_npa",
                            "housing_homelessness_npa_detail_graph_1",
                            include_accom = True, include_services=True))
        messages.extend(update_mygraph_data("housing_homelessness_npa", "housing_homelessness_npa",
                            "housing_homelessness_npa_detail_graph_2",
                            include_violence = True, include_alone=True))
        messages.extend(populate_raw_data(
                "housing_homelessness_npa", "housing_homelessness_npa",
                "housing_homelessness_npa_data",
                HousingHomelessnessNpaData, {
                    "accommodation_needs_met": "accommodation",
                    "service_needs_met": "services",
                    "clients_exp_violence": "violence",
                    "young_presenting_alone": "alone",
                }))
        messages.extend(populate_crosstab_raw_data(
                "housing_homelessness_npa", "housing_homelessness_npa",
                "data_table",
                HousingHomelessnessNpaData, {
                    "accommodation_needs_met": "accommodation",
                    "service_needs_met": "services",
                    "clients_exp_violence": "violence",
                    "young_presenting_alone": "alone",
                },
                field_map_states={
                    "accommodation_needs_met": "accommodation",
                    "clients_exp_violence": "violence",
                }))
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(update_progress("housing_homelessness_npa_state", "housing_homelessness_npa_state",
                        jurisdictions=[ state_num, AUS ],
                        pval=pval,
                        verbosity=verbosity))
            messages.extend(update_mygraph_data("homelessness_npa-housing-hero-state", "homelessness_npa-housing-hero-state",
                                "housing-hln_npa-hero-graph", 
                                include_accom = True, 
                                include_all_years=False,
                                state=state_num,
                                pval=pval))
            messages.extend(update_mygraph_data("housing_homelessness_npa_state", "housing_homelessness_npa_state",
                            "housing_homelessness_npa_summary_graph", 
                            include_accom = True, include_services=False,
                            state=state_num,
                            include_all_years=False,
                            pval=pval))
            messages.extend(update_mygraph_data("housing_homelessness_npa_state", "housing_homelessness_npa_state",
                                "housing_homelessness_npa_detail_graph_1",
                                include_accom = True, 
                                state=state_num,
                                pval=pval))
            messages.extend(update_mygraph_data("housing_homelessness_npa_state", "housing_homelessness_npa_state",
                                "housing_homelessness_npa_detail_graph_2",
                                include_violence = True, 
                                include_alone = True, 
                                state=state_num,
                                pval=pval))
            messages.extend(populate_raw_data(
                    "housing_homelessness_npa_state", "housing_homelessness_npa_state",
                    "housing_homelessness_npa_data",
                    HousingHomelessnessNpaData, {
                        "accommodation_needs_met": "accommodation",
                        "service_needs_met": "services",
                        "clients_exp_violence": "violence",
                        "young_presenting_alone": "alone",
                    },
                    pval=pval))
            messages.extend(populate_crosstab_raw_data(
                    "housing_homelessness_npa_state", "housing_homelessness_npa_state",
                    "data_table",
                    HousingHomelessnessNpaData, {
                        "accommodation_needs_met": "accommodation",
                        "service_needs_met": "services",
                        "clients_exp_violence": "violence",
                        "young_presenting_alone": "alone",
                    },
                    field_map_states={
                        "accommodation_needs_met": "accommodation",
                        "clients_exp_violence": "violence",
                    },
                    pval=pval))
    except LoaderException, e:
        raise e
# except Exception, e:
#        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_progress(widget_url, widget_lbl, jurisdictions=None, pval=None, verbosity=0):
    if jurisdictions:
        my_jurisdictions = jurisdictions
    else:
        my_jurisdictions=[NSW, VIC, QLD, WA, SA, TAS, ACT, NT, AUS]
    messages = []
    suffixes = {
        NSW: '_nsw',
        VIC: '_vic',
        QLD: '_qld',
        WA: '_wa',
        SA: '_sa',
        TAS: '_tas',
        ACT: '_act',
        NT: '_nt',
        AUS: '_aust',
    }
    progress_tlc = {
        COMPLETED: "achieved",
        IN_PROGRESS: "on_track",
        NOT_STARTED: "not_on_track",
        NOT_APPLICABLE: "not_applicable"
    }
    progress_icon = {
        COMPLETED: "yes",
        IN_PROGRESS: "yes",
        NOT_STARTED: "no",
        NOT_APPLICABLE: "unknown"
    }
    for prog in HousingHomelessnessNpaProgress.objects.filter(state__in=my_jurisdictions):
        if jurisdictions and prog.state != AUS:
            suffix = "_state"
        else:
            suffix = suffixes[prog.state]
        set_statistic_data(widget_url, widget_lbl,
                                "plan1" + suffix,
                                progress_dict[prog.plan1],
                                traffic_light_code=progress_tlc[prog.plan1],
                                icon_code=progress_icon[prog.plan1],
                                pval=pval)
        set_statistic_data(widget_url, widget_lbl,
                                "plan2" + suffix,
                                progress_dict[prog.plan2],
                                traffic_light_code=progress_tlc[prog.plan2],
                                icon_code=progress_icon[prog.plan2],
                                pval=pval)
        set_statistic_data(widget_url, widget_lbl,
                                "update" + suffix,
                                progress_dict[prog.update],
                                traffic_light_code=progress_tlc[prog.update],
                                icon_code=progress_icon[prog.update],
                                pval=pval)
        set_statistic_data(widget_url, widget_lbl,
                                "matched_funding" + suffix,
                                progress_dict[prog.matched_funding],
                                traffic_light_code=progress_tlc[prog.matched_funding],
                                icon_code=progress_icon[prog.matched_funding],
                                pval=pval)
    return messages

def update_mygraph_data(wurl, wlbl, graph_lbl, 
        include_accom=False, include_services=False, include_violence=False, include_alone=False, 
        include_all_years=True, state=0, pval=None):
    messages = []
    if not (include_accom or include_services or include_violence or include_alone):
        raise LoaderException("Must include at least one metric in graph")
    g = get_graph(wurl, wlbl, graph_lbl)
    clear_graph_data(g, clusters=True, pval=pval)
    clusters = {}
    distys = HousingHomelessnessNpaData.objects.filter(state=AUS).order_by('year', 'financial_year').distinct('year', 'financial_year')
    if not include_all_years:
        miny = distys.first().year_display()
        maxy = distys.last().year_display()
        clusters[miny] = add_graph_dyncluster(g, miny, 10, miny, pval=pval)
        clusters[maxy] = add_graph_dyncluster(g, maxy, 20, maxy, pval=pval)
    else:
        sort_order = 10
        for d in distys:
            disp = d.year_display()
            clusters[disp] = add_graph_dyncluster(g, disp, sort_order, disp, pval=pval) 
            sort_order += 10
    if state:
        for dat in HousingHomelessnessNpaData.objects.filter(state__in=(AUS, state)):
            if dat.year_display() in clusters:
                cluster = clusters[dat.year_display()]
                if dat.state == AUS:
                    suffix = "_aust"
                else:
                    suffix = "_state"
                if include_accom:
                    add_graph_data(g, "accommodation" + suffix, dat.accommodation_needs_met, cluster=cluster, pval=pval)
                if include_services:
                    add_graph_data(g, "services" + suffix, dat.service_needs_met, cluster=cluster, pval=pval)
                if include_violence:
                    add_graph_data(g, "violence" + suffix, dat.clients_exp_violence, cluster=cluster, pval=pval)
                if include_alone:
                    add_graph_data(g, "alone" + suffix, dat.young_presenting_alone, cluster=cluster, pval=pval)
    else:
        for dat in HousingHomelessnessNpaData.objects.filter(state=AUS):
            if dat.year_display() in clusters:
                cluster = clusters[dat.year_display()]
                if include_accom:
                    add_graph_data(g, "accommodation", dat.accommodation_needs_met, cluster=cluster)
                if include_services:
                    add_graph_data(g, "services", dat.service_needs_met, cluster=cluster)
                if include_violence:
                    add_graph_data(g, "violence", dat.clients_exp_violence, cluster=cluster)
                if include_alone:
                    add_graph_data(g, "alone", dat.young_presenting_alone, cluster=cluster)
    return messages

