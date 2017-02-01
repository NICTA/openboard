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
                "name": "Mean reading",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator - statistic type ("Mean scale score, reading", "Confidence interval", "RSE")'),
                            ('C', 'Row Discriminator - school year ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '12 rows per year for each possible combination of row discriminators'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "NMS reading",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator - statistic type ("Proportion at or above the national minimum standard in literacy", "Confidence interval", "RSE")'),
                            ('C', 'Row Discriminator - school year ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '12 rows per year for each possible combination of row discriminators'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Mean numeracy",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator - statistic type ("Mean scale score, numeracy", "Confidence interval", "RSE")'),
                            ('C', 'Row Discriminator - school year ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '12 rows per year for each possible combination of row discriminators'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "NMS numeracy",
                "cols": [ 
                            ('A', 'Year range e.g. 2007-09 or 2007-2009'),
                            ('B', 'Row Discriminator - statistic type ("Proportion at or above the national minimum standard in numeracy", "Confidence interval", "RSE")'),
                            ('C', 'Row Discriminator - school year ("Year 3", "Year 5", "Year 7", "Year 9")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', '12 rows per year for each possible combination of row discriminators'),
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
#    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Mean reading",
                                "Education", "NAPLAN Reading Mean Score",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_lit_score": ("Year 3", "Mean scale score, reading"),
                                    "year5_lit_score": ("Year 5", "Mean scale score, reading"),
                                    "year7_lit_score": ("Year 7", "Mean scale score, reading"),
                                    "year9_lit_score": ("Year 9", "Mean scale score, reading"),

                                    "year3_lit_score_uncertainty": ("Year 3", "Confidence interval"),
                                    "year5_lit_score_uncertainty": ("Year 5", "Confidence interval"),
                                    "year7_lit_score_uncertainty": ("Year 7", "Confidence interval"),
                                    "year9_lit_score_uncertainty": ("Year 9", "Confidence interval"),

                                    "year3_lit_score_rse": ("Year 3", "RSE"),
                                    "year5_lit_score_rse": ("Year 5", "RSE"),
                                    "year7_lit_score_rse": ("Year 7", "RSE"),
                                    "year9_lit_score_rse": ("Year 9", "RSE"),
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "NMS reading",
                                "Education", "NAPLAN Reading NMS",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_lit_nms": ("Year 3", "Proportion at or above the national minimum standard in literacy"),
                                    "year5_lit_nms": ("Year 5", "Proportion at or above the national minimum standard in literacy"),
                                    "year7_lit_nms": ("Year 7", "Proportion at or above the national minimum standard in literacy"),
                                    "year9_lit_nms": ("Year 9", "Proportion at or above the national minimum standard in literacy"),

                                    "year3_lit_nms_uncertainty": ("Year 3", "Confidence interval"),
                                    "year5_lit_nms_uncertainty": ("Year 5", "Confidence interval"),
                                    "year7_lit_nms_uncertainty": ("Year 7", "Confidence interval"),
                                    "year9_lit_nms_uncertainty": ("Year 9", "Confidence interval"),

                                    "year3_lit_nms_rse": ("Year 3", "RSE"),
                                    "year5_lit_nms_rse": ("Year 5", "RSE"),
                                    "year7_lit_nms_rse": ("Year 7", "RSE"),
                                    "year9_lit_nms_rse": ("Year 9", "RSE"),
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "Mean numeracy",
                                "Education", "NAPLAN Numeracy Mean Score",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_num_score": ("Year 3", "Mean scale score, numeracy"),
                                    "year5_num_score": ("Year 5", "Mean scale score, numeracy"),
                                    "year7_num_score": ("Year 7", "Mean scale score, numeracy"),
                                    "year9_num_score": ("Year 9", "Mean scale score, numeracy"),

                                    "year3_num_score_uncertainty": ("Year 3", "Confidence interval"),
                                    "year5_num_score_uncertainty": ("Year 5", "Confidence interval"),
                                    "year7_num_score_uncertainty": ("Year 7", "Confidence interval"),
                                    "year9_num_score_uncertainty": ("Year 9", "Confidence interval"),

                                    "year3_num_score_rse": ("Year 3", "RSE"),
                                    "year5_num_score_rse": ("Year 5", "RSE"),
                                    "year7_num_score_rse": ("Year 7", "RSE"),
                                    "year9_num_score_rse": ("Year 9", "RSE"),
                                },
                                verbosity))
        messages.extend(
                load_state_grid(wb, "NMS numeracy",
                                "Education", "NAPLAN Numeracy NMS",
                                None, EducationNaplanData,
                                {}, {
                                    "year3_num_nms": ("Year 3", "Proportion at or above the national minimum standard in numeracy"),
                                    "year5_num_nms": ("Year 5", "Proportion at or above the national minimum standard in numeracy"),
                                    "year7_num_nms": ("Year 7", "Proportion at or above the national minimum standard in numeracy"),
                                    "year9_num_nms": ("Year 9", "Proportion at or above the national minimum standard in numeracy"),

                                    "year3_num_nms_uncertainty": ("Year 3", "Confidence interval"),
                                    "year5_num_nms_uncertainty": ("Year 5", "Confidence interval"),
                                    "year7_num_nms_uncertainty": ("Year 7", "Confidence interval"),
                                    "year9_num_nms_uncertainty": ("Year 9", "Confidence interval"),

                                    "year3_num_nms_rse": ("Year 3", "RSE"),
                                    "year5_num_nms_rse": ("Year 5", "RSE"),
                                    "year7_num_nms_rse": ("Year 7", "RSE"),
                                    "year9_num_nms_rse": ("Year 9", "RSE"),
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
                                EducationNaplanData, [
                                        ( "year3_lit_nms", "year3_lit_nms_uncertainty", "year3_lit_nms_rse"), 
                                        ( "year5_lit_nms", "year5_lit_nms_uncertainty", "year5_lit_nms_rse"), 
                                        ( "year7_lit_nms", "year7_lit_nms_uncertainty", "year7_lit_nms_rse"), 
                                        ( "year9_lit_nms", "year9_lit_nms_uncertainty", "year9_lit_nms_rse"), 
                                        ( "year3_lit_score", "year3_lit_score_uncertainty", "year3_lit_score_rse"), 
                                        ( "year5_lit_score", "year5_lit_score_uncertainty", "year5_lit_score_rse"), 
                                        ( "year7_lit_score", "year7_lit_score_uncertainty", "year7_lit_score_rse"), 
                                        ( "year9_lit_score", "year9_lit_score_uncertainty", "year9_lit_score_rse"), 
                                ],
                                verbosity=verbosity))
        messages.extend(update_state_stats(
                                "naplan_num-education-hero-state", "naplan_num-education-hero-state", 
                                "education_naplan_num_state", "education_naplan_num_state",
                                EducationNaplanData, [
                                        ( "year3_num_nms", "year3_num_nms_uncertainty", "year3_num_nms_rse"), 
                                        ( "year5_num_nms", "year5_num_nms_uncertainty", "year5_num_nms_rse"), 
                                        ( "year7_num_nms", "year7_num_nms_uncertainty", "year7_num_nms_rse"), 
                                        ( "year9_num_nms", "year9_num_nms_uncertainty", "year9_num_nms_rse"), 
                                        ( "year3_num_score", "year3_num_score_uncertainty", "year3_num_score_rse"), 
                                        ( "year5_num_score", "year5_num_score_uncertainty", "year5_num_score_rse"), 
                                        ( "year7_num_score", "year7_num_score_uncertainty", "year7_num_score_rse"), 
                                        ( "year9_num_score", "year9_num_score_uncertainty", "year9_num_score_rse"), 
                                ],
                                verbosity=verbosity))
        messages.extend(update_naplan_graphs("lit", AUS, verbosity))
        messages.extend(update_naplan_graphs("num", AUS, verbosity))
        messages.extend(
                populate_raw_data(
                    "education_naplan_lit", "education_naplan_lit",
                    "education_naplan_lit", EducationNaplanData,
                    {
                        "year3_lit_score": "yr3_avg_score",
                        "year5_lit_score": "yr5_avg_score",
                        "year7_lit_score": "yr7_avg_score",
                        "year9_lit_score": "yr9_avg_score",
                        "year3_lit_nms": "yr3_nms",
                        "year5_lit_nms": "yr5_nms",
                        "year7_lit_nms": "yr7_nms",
                        "year9_lit_nms": "yr9_nms",
                    })
        )
        messages.extend(
                populate_raw_data(
                    "education_naplan_num", "education_naplan_num",
                    "education_naplan_num", EducationNaplanData,
                    {
                        "year3_num_score": "yr3_avg_score",
                        "year5_num_score": "yr5_avg_score",
                        "year7_num_score": "yr7_avg_score",
                        "year9_num_score": "yr9_avg_score",
                        "year3_num_nms": "yr3_nms",
                        "year5_num_nms": "yr5_nms",
                        "year7_num_nms": "yr7_nms",
                        "year9_num_nms": "yr9_nms",
                    })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(update_naplan_graphs("lit", state_num, verbosity, pval=pval))
            messages.extend(update_naplan_graphs("num", state_num, verbosity, pval=pval))
            messages.extend(
                        populate_raw_data(
                            "education_naplan_lit", "education_naplan_lit",
                            "education_naplan_lit", EducationNaplanData,
                            {
                                "year3_lit_score": "yr3_avg_score",
                                "year5_lit_score": "yr5_avg_score",
                                "year7_lit_score": "yr7_avg_score",
                                "year9_lit_score": "yr9_avg_score",
                                "year3_lit_nms": "yr3_nms",
                                "year5_lit_nms": "yr5_nms",
                                "year7_lit_nms": "yr7_nms",
                                "year9_lit_nms": "yr9_nms",
                            }, pval=pval)
            )
            messages.extend(
                        populate_raw_data(
                            "education_naplan_num", "education_naplan_num",
                            "education_naplan_num", EducationNaplanData,
                            {
                                "year3_num_score": "yr3_avg_score",
                                "year5_num_score": "yr5_avg_score",
                                "year7_num_score": "yr7_avg_score",
                                "year9_num_score": "yr9_avg_score",
                                "year3_num_nms": "yr3_nms",
                                "year5_num_nms": "yr5_nms",
                                "year7_num_nms": "yr7_nms",
                                "year9_num_nms": "yr9_nms",
                            }, pval=pval)
            )
#   except LoaderException, e:
#        raise e
#    except Exception, e:
#        raise LoaderException("Invalid file: %s" % unicode(e))
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

