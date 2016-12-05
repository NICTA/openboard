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
from education_naplan_uploader.models import *
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
                "name": "Data1",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Quartets of rows per year, average score in reading per NAPLAN school year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Data2",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Quartets of rows per year, proportion meeting minimum reading standard per NAPLAN school year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Data3",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Quartets of rows per year, average score in numeracy per NAPLAN school year'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Data4",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Quartets of rows per year, proportion meeting minimum maths standard per NAPLAN school year'),
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
                            ('Literacy', 'Additional Desc Body text for literacy widgets. One paragraph per line'),
                            ('Numeracy', 'Additional Desc Body text for numeracy widgets. One paragraph per line'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

indicators_lit = "Improve the literacy achievement of Year 3,5,7 and 9 students in national testing"
indicators_num = "Improve the numeracy achievement of Year 3,5,7 and 9 students in national testing"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data1",
                                "Education", "NAPLAN Reading Avg Score",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_lit_score": "Year 3", 
                                    "year5_lit_score": "Year 5",
                                    "year7_lit_score": "Year 7",
                                    "year9_lit_score": "Year 9",
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "Data2",
                                "Education", "NAPLAN Reading NMS",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_lit_nms": "Year 3", 
                                    "year5_lit_nms": "Year 5",
                                    "year7_lit_nms": "Year 7",
                                    "year9_lit_nms": "Year 9",
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "Data3",
                                "Education", "NAPLAN Numeracy Avg Score",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_num_score": "Year 3", 
                                    "year5_num_score": "Year 5",
                                    "year7_num_score": "Year 7",
                                    "year9_num_score": "Year 9",
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "Data4",
                                "Education", "NAPLAN Numeracy NMS",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_num_nms": "Year 3", 
                                    "year5_num_nms": "Year 5",
                                    "year7_num_nms": "Year 7",
                                    "year9_num_nms": "Year 9",
                                },
                                verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True, additional_lookups={
                        "literacy": "literacy",
                        "numeracy": "numeracy",
                })
        messages.extend(update_stats(desc, indicators_lit,
                                "naplan_lit-education-hero", "naplan_lit-education-hero", 
                                "naplan_lit-education-hero-state", "naplan_lit-education-hero-state", 
                                "education_naplan_lit", "education_naplan_lit",
                                "education_naplan_lit_state", "education_naplan_lit_state",
                                verbosity,
                                additional_desc_body="literacy"))
        messages.extend(update_stats(desc, indicators_num,
                                "naplan_num-education-hero", "naplan_num-education-hero", 
                                "naplan_num-education-hero-state", "naplan_num-education-hero-state", 
                                "education_naplan_num", "education_naplan_num",
                                "education_naplan_num_state", "education_naplan_num_state",
                                verbosity,
                                additional_desc_body="numeracy"))
        messages.extend(update_state_stats(
                                "naplan_lit-education-hero-state", "naplan_lit-education-hero-state", 
                                "education_naplan_lit_state", "education_naplan_lit_state",
                                None, None, None,
                                override_status="mixed_results",
                                verbosity=verbosity))
        messages.extend(update_state_stats(
                                "naplan_num-education-hero-state", "naplan_num-education-hero-state", 
                                "education_naplan_num_state", "education_naplan_num_state",
                                None, None, None,
                                override_status="mixed_results",
                                verbosity=verbosity))
        messages.extend(update_naplan_graphs("lit", AUS, verbosity))
        messages.extend(update_naplan_graphs("num", AUS, verbosity))
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(update_naplan_graphs("lit", state_num, verbosity, pval=pval))
            messages.extend(update_naplan_graphs("num", state_num, verbosity, pval=pval))
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_naplan_graph_data(wurl, wlbl, graph, model, fields, state_num, verbosity=0, pval=None):
    messages = []
    if verbosity > 2:
        messages.append("Updating graph %s:%s (%d)" % (wurl, graph, state_num))
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    qry = model.objects.filter(state=state_num)
    for o in qry:
        for ds, fld in fields.items():
            add_graph_data(g, ds, getattr(o, fld), horiz_value=o.year_as_date(), pval=pval)
    return messages


def update_naplan_graphs(metric_abbrev, state, verbosity=0, pval=None):
    messages = []
    if verbosity > 2:
        messages.append("Updating graphs for %s, %d" % (metric_abbrev, state))
    if pval:
        hero_suffix="-state"
        detl_suffix="_state"
    else:
        hero_suffix=""
        detl_suffix=""
    for wurl, graph in [
                    ("naplan_%s-education-hero%s" % (metric_abbrev,hero_suffix), "education-naplan_%s-hero-graph" % metric_abbrev),
                    ("education_naplan_%s%s" % (metric_abbrev,detl_suffix), "education_naplan_%s_summary_graph" % metric_abbrev),
                    ("education_naplan_%s%s" % (metric_abbrev,detl_suffix), "education_naplan_%s_detail_graph" % metric_abbrev),
                ]:
        messages.extend(
                update_naplan_graph_data(wurl, wurl, graph,
                            EducationNaplanData, 
                            { 
                                "year3": "year3_%s_nms" % metric_abbrev,
                                "year5": "year5_%s_nms" % metric_abbrev,
                                "year7": "year7_%s_nms" % metric_abbrev,
                                "year9": "year9_%s_nms" % metric_abbrev,
                            },
                            state,
                            verbosity=verbosity,
                            pval=pval)
        )
    messages.extend(
                update_naplan_graph_data(
                            "education_naplan_%s%s" % (metric_abbrev, detl_suffix), 
                            "education_naplan_%s%s" % (metric_abbrev, detl_suffix), 
                            "education_naplan_%s_avgscore_graph" % metric_abbrev,
                            EducationNaplanData, 
                            { 
                                "year3": "year3_%s_score" % metric_abbrev,
                                "year5": "year5_%s_score" % metric_abbrev,
                                "year7": "year7_%s_score" % metric_abbrev,
                                "year9": "year9_%s_score" % metric_abbrev,
                            },
                            state,
                            verbosity=verbosity,
                            pval=pval)
    )
    return messages

