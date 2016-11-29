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
from education_participation_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, indicator_tlc_trend
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
                            ('B', 'Row Discriminator ("Full-time study", "Full-time work", "Combination of study and work", "Not fully engaged")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Quartets of rows per year, one for engagement category'),
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
                        ],
                "notes": [
                         ],
            }
        ],
}

indicators = "Improve the proportion of young people participating in post-school education, training or employment"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Education", "Post-school participation",
                                None, EducationParticipationData,
                                {}, {
                                    "study": "Full-time study", 
                                    "work": "Full-time work",
                                    "study_work": "Combination of study and work",
                                    "not_engaged": "Not fully engaged",
                                },
                                verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicators,
                                "participation-education-hero", "participation-education-hero", 
                                "participation-education-hero-state", "participation-education-hero-state", 
                                "education_participation", "education_participation",
                                "education_participation_state", "education_participation_state",
                                verbosity))
        aust_q = EducationParticipationData.objects.filter(state=AUS).order_by("year")
        aust_ref = aust_q.first()
        aust_latest = aust_q.last()
        aust_tlc, aust_trend = indicator_tlc_trend(aust_ref.engaged(), aust_latest.engaged())
        set_statistic_data('participation-education-hero', 'participation-education-hero',
                        'reference', aust_ref.engaged(),
                        label=aust_ref.year_display(),
                        traffic_light_code=aust_tlc)
        set_statistic_data('participation-education-hero', 'participation-education-hero',
                        'latest', aust_latest.engaged(),
                        traffic_light_code=aust_tlc,
                        label=aust_latest.year_display(),
                        trend=aust_trend)
        set_statistic_data('education_participation', 'education_participation',
                        'reference', aust_ref.engaged(),
                        label=aust_ref.year_display(),
                        traffic_light_code=aust_tlc)
        set_statistic_data('education_participation', 'education_participation',
                        'latest', aust_latest.engaged(),
                        traffic_light_code=aust_tlc,
                        label=aust_latest.year_display(),
                        trend=aust_trend)
        messages.extend(
                update_graph_data(
                            'education_participation', 'education_participation',
                            "education_participation_detail_graph",
                            EducationParticipationData, "engaged",
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_q = EducationParticipationData.objects.filter(state=state_num).order_by("year")
            state_ref = state_q.first()
            state_latest = state_q.last()
            state_tlc, state_trend = indicator_tlc_trend(state_ref.engaged(), state_latest.engaged())
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'reference', aust_ref.engaged(),
                            traffic_light_code=aust_tlc,
                            pval=pval)
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'latest', aust_latest.engaged(),
                            traffic_light_code=aust_tlc,
                            trend=aust_trend,
                            pval=pval)
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'reference_state', state_ref.engaged(),
                            traffic_light_code=state_tlc,
                            pval=pval)
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'latest_state', state_latest.engaged(),
                            traffic_light_code=aust_tlc,
                            trend=state_trend,
                            pval=pval)
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'ref_year', state_ref.year_display(),
                            pval=pval)
            set_statistic_data(
                            'participation-education-hero-state', 'participation-education-hero-state',
                            'curr_year', state_latest.year_display(),
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'reference', aust_ref.engaged(),
                            traffic_light_code=aust_tlc,
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'latest', aust_latest.engaged(),
                            traffic_light_code=aust_tlc,
                            trend=aust_trend,
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'reference_state', state_ref.engaged(),
                            traffic_light_code=state_tlc,
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'latest_state', state_latest.engaged(),
                            traffic_light_code=aust_tlc,
                            trend=state_trend,
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'ref_year', state_ref.year_display(),
                            pval=pval)
            set_statistic_data('education_participation_state', 'education_participation_state',
                            'curr_year', state_latest.year_display(),
                            pval=pval)
            messages.extend(
                    update_my_state_graph(
                            'education_participation_state', 'education_participation_state',
                            'education_participation_detail_graph',
                            aust_ref, aust_latest, 'australia',
                            state_ref, state_latest, 'state',
                            pval, 
                            verbosity)
                    ) 
    except LoaderException, e:
        raise e
#except Exception, e:
#        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_state_graph(wurl, wlbl, graph, 
                aref, alat, acluster, sref, slat, scluster, 
                pval, verbosity=0):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    add_graph_data(g, 'reference', aref.engaged(), cluster=acluster, pval=pval)
    add_graph_data(g, 'latest_year', alat.engaged(), cluster=acluster, pval=pval)
    add_graph_data(g, 'reference', sref.engaged(), cluster=scluster, pval=pval)
    add_graph_data(g, 'latest_year', slat.engaged(), cluster=scluster, pval=pval)

    set_dataset_override(g, "reference", aref.year_display(), pval=pval)
    set_dataset_override(g, "latest_year", alat.year_display(), pval=pval)
    return messages
