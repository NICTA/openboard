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
from health_edwait_uploader.models import *
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
                            ('B', 'Row Discriminator ("Patients treated within national benchmarks for emergency department waiting time (%)")',),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Rows per year'),
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
                            ('Measure', 'Full description of benchmark'),
                            ('Short Title', 'Short widget title (not used)'),
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

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Health", "Emergency Dept waiting times",
                                None, HealthEmergencyWaitData,
                                {}, {
                                    "treated_ontime": "Patients treated within national benchmarks for emergency department waiting time (%)",
                                },
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, None,
                                "edwait-health-hero", "edwait-health-hero", 
                                "edwait-health-hero-state", "edwait-health-hero-state", 
                                "health_edwait", "health_edwait",
                                "health_edwait_state", "health_edwait_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "edwait-health-hero-state", "edwait-health-hero-state", 
                                "health_edwait_state", "health_edwait_state",
                                HealthEmergencyWaitData, [("treated_ontime", None,),],
                                verbosity=verbosity))
        aust_q = HealthEmergencyWaitData.objects.filter(state=AUS).order_by("year")
        aust_ref = aust_q.first()
        aust_latest = aust_q.last()
        aust_tlc, aust_trend = indicator_tlc_trend(aust_ref.treated_ontime, aust_latest.treated_ontime)
        set_statistic_data('edwait-health-hero', 'edwait-health-hero',
                        'reference', aust_ref.treated_ontime,
                        label=aust_ref.year_display(),
                        traffic_light_code=aust_tlc)
        set_statistic_data('edwait-health-hero', 'edwait-health-hero',
                        'latest', aust_latest.treated_ontime,
                        traffic_light_code=aust_tlc,
                        label=aust_latest.year_display(),
                        trend=aust_trend)
        set_statistic_data("health_edwait", "health_edwait",
                        'reference', aust_ref.treated_ontime,
                        label=aust_ref.year_display(),
                        traffic_light_code=aust_tlc)
        set_statistic_data("health_edwait", "health_edwait",
                        'latest', aust_latest.treated_ontime,
                        traffic_light_code=aust_tlc,
                        label=aust_latest.year_display(),
                        trend=aust_trend)
        messages.extend(
                update_graph_data(
                            "health_edwait", "health_edwait",
                            "health_edwait_detail_graph",
                            HealthEmergencyWaitData, "treated_ontime",
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data("health_edwait", "health_edwait",
                                "health_edwait", HealthEmergencyWaitData, 
                                {
                                    "treated_ontime": "percentage_ontime",
                                })
        )
        messages.extend(
                populate_crosstab_raw_data("health_edwait", "health_edwait",
                                "data_table", HealthEmergencyWaitData,
                                {
                                    "treated_ontime": "percent",
                                })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_q = HealthEmergencyWaitData.objects.filter(state=state_num).order_by("year")
            state_ref = state_q.first()
            state_latest = state_q.last()
            state_tlc, state_trend = indicator_tlc_trend(state_ref.treated_ontime, state_latest.treated_ontime)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'reference', aust_ref.treated_ontime,
                            traffic_light_code=aust_tlc,
                            pval=pval)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'latest', aust_latest.treated_ontime,
                            traffic_light_code=aust_tlc,
                            trend=aust_trend,
                            pval=pval)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'reference_state', state_ref.treated_ontime,
                            traffic_light_code=state_tlc,
                            pval=pval)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'latest_state', state_latest.treated_ontime,
                            traffic_light_code=state_tlc,
                            trend=state_trend,
                            pval=pval)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'ref_year', state_ref.year_display(),
                            pval=pval)
            set_statistic_data(
                            "edwait-health-hero-state", "edwait-health-hero-state", 
                            'curr_year', state_latest.year_display(),
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'reference', aust_ref.treated_ontime,
                            traffic_light_code=aust_tlc,
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'latest', aust_latest.treated_ontime,
                            traffic_light_code=aust_tlc,
                            trend=aust_trend,
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'reference_state', state_ref.treated_ontime,
                            traffic_light_code=state_tlc,
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'latest_state', state_latest.treated_ontime,
                            traffic_light_code=aust_tlc,
                            trend=state_trend,
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'ref_year', state_ref.year_display(),
                            pval=pval)
            set_statistic_data("health_edwait_state", "health_edwait_state",
                            'curr_year', state_latest.year_display(),
                            pval=pval)
            messages.extend(
                    update_my_state_graph(
                            "health_edwait_state", "health_edwait_state",
                            'health_edwait_detail_graph',
                            aust_ref, aust_latest, 'australia',
                            state_ref, state_latest, 'state',
                            pval, 
                            verbosity)
                    ) 
            messages.extend(
                populate_raw_data("health_edwait_state", "health_edwait_state",
                                "health_edwait", HealthEmergencyWaitData, 
                                {
                                    "treated_ontime": "percentage_ontime",
                                }, pval=pval)
            )
            messages.extend(
                populate_crosstab_raw_data("health_edwait_state", "health_edwait_state",
                                "data_table", HealthEmergencyWaitData,
                                {
                                    "treated_ontime": "percent",
                                }, pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_my_state_graph(wurl, wlbl, graph, 
                aref, alat, acluster, sref, slat, scluster, 
                pval, verbosity=0):
    messages = []
    g = get_graph(wurl, wlbl, graph)
    clear_graph_data(g, pval=pval)
    add_graph_data(g, 'reference', aref.treated_ontime, cluster=acluster, pval=pval)
    add_graph_data(g, 'latest_year', alat.treated_ontime, cluster=acluster, pval=pval)
    add_graph_data(g, 'reference', sref.treated_ontime, cluster=scluster, pval=pval)
    add_graph_data(g, 'latest_year', slat.treated_ontime, cluster=scluster, pval=pval)

    set_dataset_override(g, "reference", aref.year_display(), pval=pval)
    set_dataset_override(g, "latest_year", alat.year_display(), pval=pval)
    return messages
