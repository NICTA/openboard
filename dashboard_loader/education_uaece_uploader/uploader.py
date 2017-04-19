#   Copyright 2017 CSIRO
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


from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from education_uaece_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats, indicator_tlc_trend
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
                            ('A', 'Year e.g. 2008'),
                            ('B', 'Row Discriminator - must be "Proportion of children (%)"'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Row per year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                    'Aust column may be blank.',
                    '"National Benchmark" row may be supplied, but is ignored'
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
                            ('Status', 'Indicator status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of indicator status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                            ('WA, Vic, NSW, etc.', 'Additional comments for individual states. One paragraph per line. (optional)'),
                        ],
                "notes": [
                         ],
            }
        ],
}

benchmark = "95 per cent of children enrolled in a quality preschool program in the year before full-time school."

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Education", "Universal Access to Early Childhood Education",
                                None, AccessEceData,
                                {}, {
                                    "enrolled": "Proportion of children (%)", 
                                },
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                                "uaece-education-hero", "uaece-education-hero", 
                                "uaece-education-hero-state", "uaece-education-hero-state", 
                                "education_uaece", "education_uaece",
                                "education_uaece_state", "education_uaece_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "uaece-education-hero-state", "uaece-education-hero-state", 
                                "education_uaece_state", "education_uaece_state",
                                AccessEceData, [ ],
                                use_benchmark_tls=True,
                                status_func=AccessEceData.tlc,
                                verbosity=verbosity))
        latest_year = AccessEceData.objects.all().last().year
        jurisdictions_met = AccessEceData.objects.filter(year=latest_year, enrolled__gte=95).count()
        set_statistic_data("uaece-education-hero", "uaece-education-hero", 
                        "jurisdictions_met",
                        jurisdictions_met,
                        traffic_light_code=desc["status"]["tlc"])
        set_statistic_data("uaece-education-hero", "uaece-education-hero", 
                        "target",
                        95,
                        traffic_light_code="new_benchmark")
        set_statistic_data("education_uaece", "education_uaece",
                        "jurisdictions_met",
                        jurisdictions_met,
                        traffic_light_code=desc["status"]["tlc"])
        set_statistic_data("education_uaece", "education_uaece",
                        "target",
                        95,
                        traffic_light_code="new_benchmark")
        messages.extend(populate_my_graph("education_uaece", "education_uaece_detail_graph"))
        messages.extend(
                populate_raw_data("education_uaece", "education_uaece",
                                "education_uaece", AccessEceData,
                                {
                                    "enrolled": "proportion",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data("education_uaece", "education_uaece",
                                "data_table", AccessEceData,
                                {
                                    "enrolled": "proportion",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_latest = AccessEceData.objects.get(year=latest_year, state=state_num)
            set_statistic_data("uaece-education-hero-state", "uaece-education-hero-state", 
                        "proportion_enrolled",
                        int(state_latest.enrolled),
                        traffic_light_code=state_latest.tlc(),
                        pval=pval)
            set_statistic_data("uaece-education-hero-state", "uaece-education-hero-state", 
                        "target",
                        95,
                        traffic_light_code="new_benchmark",
                        pval=pval)
            set_statistic_data("education_uaece_state", "education_uaece_state",
                        "proportion_enrolled",
                        int(state_latest.enrolled),
                        traffic_light_code=state_latest.tlc(),
                        pval=pval)
            set_statistic_data("education_uaece_state", "education_uaece_state",
                        "target",
                        95,
                        traffic_light_code="new_benchmark",
                        pval=pval)
            messages.extend(populate_my_graph("education_uaece_state", "education_uaece_detail_graph", 
                            state_num=state_num,
                            pval=pval))
            messages.extend(
                    populate_raw_data("education_uaece_state", "education_uaece_state",
                            "education_uaece", AccessEceData,
                            {
                                "enrolled": "proportion",
                            },
                            pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data("education_uaece_state", "education_uaece_state",
                            "data_table", AccessEceData,
                            {
                                "enrolled": "proportion",
                            },
                            pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def populate_my_graph(wurl, graph, state_num=None, pval=None):
    messages = []
    g = get_graph(wurl, wurl, graph)
    clear_graph_data(g, pval=pval)
    year_map = {
        2008: "reference",
        2014: "recent",
        2015: "latest"
    }
    if pval:
        qry = AccessEceData.objects.filter(state=state_num)
    else:
        qry = AccessEceData.objects.all()
    for o in qry:
        if pval:
            cluster = "state"
        else:
            cluster = o.state_display().lower()
        if o.year in year_map:
            add_graph_data(g, year_map[o.year], o.enrolled, cluster=cluster, pval=pval)
        else:
    for y, ds in year_map.items():
        set_dataset_override(g, ds, unicode(y))
    return messages

