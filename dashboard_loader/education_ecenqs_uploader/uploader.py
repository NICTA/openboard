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


from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from education_ecenqs_uploader.models import *
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
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator ("No rating", "Working towards NQS", "Meeting NQS"'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for NQS status'),
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
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                            ('WA, Vic, NSW, etc.', 'Additional comments for individual states. One paragraph per line. (optional)'),
                        ],
                "notes": [
                         ],
            }
        ],
}

indicators = "Improve the proportion of early childhood education and care services meeting the National Quality Standards"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Education", "Early Childhood Education National Quality Standard",
                                None, EducationEceNqsData,
                                {}, {
                                    "meeting_nqs": "Meeting NQS", 
                                    "working_towards": "Working towards NQS",
                                    "no_rating": "No rating",
                                },
                                verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicators,
                                "ecenqs-education-hero", "ecenqs-education-hero", 
                                "ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                                "education_ecenqs", "education_ecenqs",
                                "education_ecenqs_state", "education_ecenqs_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                                "education_ecenqs_state", "education_ecenqs_state",
                                EducationEceNqsData, [ ("meeting_nqs_pct", None,),],
                                verbosity=verbosity))
        aust_data = get_values(AUS)
        set_statistic_data("ecenqs-education-hero", "ecenqs-education-hero", 
                    "reference",
                    aust_data["ref"]["val"],
                    label=aust_data["ref"]["year"],
                    traffic_light_code=aust_data["tlc"])
        set_statistic_data("ecenqs-education-hero", "ecenqs-education-hero", 
                    "meeting_nqs",
                    aust_data["latest"]["val"],
                    label=aust_data["latest"]["year"],
                    traffic_light_code=aust_data["tlc"],
                    trend=aust_data["trend"])
        set_statistic_data("education_ecenqs", "education_ecenqs",
                    "reference",
                    aust_data["ref"]["val"],
                    label=aust_data["ref"]["year"],
                    traffic_light_code=aust_data["tlc"])
        set_statistic_data("education_ecenqs", "education_ecenqs",
                    "meeting_nqs",
                    aust_data["latest"]["val"],
                    label=aust_data["latest"]["year"],
                    traffic_light_code=aust_data["tlc"],
                    trend=aust_data["trend"])
        messages.extend(populate_graph("education_ecenqs", "education_ecenqs_detail_graph", aust_data["ref"]["obj"].year, aust_data["latest"]["obj"].year))
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_data = get_values(state_num)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "ref_year",
                        aust_data["ref"]["year"],
                        pval=pval)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "curr_year",
                        aust_data["latest"]["year"],
                        pval=pval)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "reference",
                        aust_data["ref"]["val"],
                        traffic_light_code=aust_data["tlc"],
                        pval=pval)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "meeting_nqs",
                        aust_data["latest"]["val"],
                        traffic_light_code=aust_data["tlc"],
                        trend=aust_data["trend"],
                        pval=pval)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "reference_state",
                        state_data["ref"]["val"],
                        traffic_light_code=state_data["tlc"],
                        pval=pval)
            set_statistic_data("ecenqs-education-hero-state", "ecenqs-education-hero-state", 
                        "meeting_nqs_state",
                        aust_data["latest"]["val"],
                        traffic_light_code=state_data["tlc"],
                        trend=state_data["trend"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "ref_year",
                        aust_data["ref"]["year"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "curr_year",
                        aust_data["latest"]["year"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "reference",
                        aust_data["ref"]["val"],
                        traffic_light_code=aust_data["tlc"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "meeting_nqs",
                        aust_data["latest"]["val"],
                        traffic_light_code=aust_data["tlc"],
                        trend=aust_data["trend"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "reference_state",
                        state_data["ref"]["val"],
                        traffic_light_code=state_data["tlc"],
                        pval=pval)
            set_statistic_data("education_ecenqs_state", "education_ecenqs_state",
                        "meeting_nqs_state",
                        state_data["latest"]["val"],
                        traffic_light_code=state_data["tlc"],
                        trend=state_data["trend"],
                        pval=pval)
            messages.extend(populate_graph("education_ecenqs_state", "education_ecenqs_detail_graph", 
                            aust_data["ref"]["obj"].year, aust_data["latest"]["obj"].year, 
                            pval=pval))
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def get_values(state):
    qry = EducationEceNqsData.objects.filter(state=state).order_by("year")
    ref = qry.first()
    latest = qry.last()
    data = {
        "ref": {
            "obj": ref,
            "val": ref.meeting_nqs_pct(),
            "year": ref.year_display()
        },
        "latest": {
            "obj": latest,
            "val": latest.meeting_nqs_pct(),
            "year": latest.year_display()
        }
    }
    data["tlc"], data["trend"] = indicator_tlc_trend(ref.meeting_nqs_pct(), latest.meeting_nqs_pct())
    return data

def populate_graph(wurl, graph, ref_year, latest_year, pval=None):
    messages = []
    g = get_graph(wurl, wurl, graph)
    clear_graph_data(g, pval=pval)
    for o in EducationEceNqsData.objects.all():
        if o.year == ref_year:
            ds = "reference"
        elif o.year == latest_year:
            ds = "latest"
        else:
            continue
        add_graph_data(g, ds, o.meeting_nqs_pct(), cluster=o.state_display().lower(), pval=pval)
    set_dataset_override(g, "reference", unicode(ref_year), pval=pval)
    set_dataset_override(g, "latest", unicode(latest_year), pval=pval)
    return messages
