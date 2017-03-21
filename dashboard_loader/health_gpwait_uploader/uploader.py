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
from health_gpwait_uploader.models import *
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
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("Within four hours", "Four to less than 24 hours", "24 hours of more")',),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one per allowed value of row discriminator'),
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
                                "Health", "GP waiting times",
                                None, HealthGPWaitData,
                                {}, {
                                    "treated_within_4h": "Within four hours",
                                    "treated_4_24h": "Four to less than 24 hours",
                                    "treated_over_24h": "24 hours or more",
                                },
                                verbosity=verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, None,
                                "gpwait-health-hero", "gpwait-health-hero", 
                                "gpwait-health-hero-state", "gpwait-health-hero-state", 
                                "health_gpwait", "health_gpwait",
                                "health_gpwait_state", "health_gpwait_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "gpwait-health-hero-state", "gpwait-health-hero-state", 
                                "health_gpwait_state", "health_gpwait_state",
                                HealthGPWaitData, [
                                    ("treated_within_4h", None,),
                                    ("treated_over_24h", None,),
                                ],
                                want_increase = [ True, False ],
                                verbosity=verbosity))
        aust_q = HealthGPWaitData.objects.filter(state=AUS).order_by("year")
        aust_ref = aust_q.first()
        aust_latest = aust_q.last()
        aust_4h_tlc, aust_4h_trend = indicator_tlc_trend(aust_ref.treated_within_4h, aust_latest.treated_within_4h)
        aust_24h_tlc, aust_24h_trend = indicator_tlc_trend(aust_ref.treated_over_24h, aust_latest.treated_over_24h, want_increase=False)
        set_statistic_data('gpwait-health-hero', 'gpwait-health-hero',
                        'within_4_hrs', aust_latest.treated_within_4h,
                        label="Within 4 hrs (%s)" % aust_latest.year_display(),
                        trend=aust_4h_trend,
                        traffic_light_code=aust_4h_tlc)
        set_statistic_data('gpwait-health-hero', 'gpwait-health-hero',
                        'over_24_hrs', aust_latest.treated_over_24h,
                        label="Over 24 hrs (%s)" % aust_latest.year_display(),
                        traffic_light_code=aust_24h_tlc,
                        trend=aust_24h_trend)
        set_statistic_data("health_gpwait", "health_gpwait",
                        'within_4_hrs', aust_latest.treated_within_4h,
                        label="Within 4 hrs (%s)" % aust_latest.year_display(),
                        trend=aust_4h_trend,
                        traffic_light_code=aust_4h_tlc)
        set_statistic_data("health_gpwait", "health_gpwait",
                        'over_24_hrs', aust_latest.treated_over_24h,
                        label="Over 24 hrs (%s)" % aust_latest.year_display(),
                        traffic_light_code=aust_24h_tlc,
                        trend=aust_24h_trend)
        messages.extend(
                update_graph_data(
                            "health_gpwait", "health_gpwait",
                            "health_wait_detail_graph_4hrs",
                            HealthGPWaitData, "treated_within_4h",
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "health_gpwait", "health_gpwait",
                            "health_wait_detail_graph_24hrs",
                            HealthGPWaitData, "treated_over_24h",
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data("health_gpwait", "health_gpwait",
                                "health_gpwait", HealthGPWaitData, 
                                {
                                    "treated_within_4h": "percentage_within_4_hrs",
                                    "treated_4_24h": "percentage_4_to_24_hrs",
                                    "treated_over_24h": "percentage_over_24_hrs",
                                })
        )
        messages.extend(
                populate_crosstab_raw_data("health_gpwait", "health_gpwait",
                                "data_table", HealthGPWaitData,
                                {
                                    "treated_within_4h": "within_4_hrs",
                                    "treated_4_24h": "4_to_24_hrs",
                                    "treated_over_24h": "over_24_hrs",
                                })
        )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            state_q = HealthGPWaitData.objects.filter(state=state_num).order_by("year")
            state_ref = state_q.first()
            state_latest = state_q.last()
            state_4h_tlc, state_4h_trend = indicator_tlc_trend(state_ref.treated_within_4h, state_latest.treated_within_4h)
            state_24h_tlc, state_24h_trend = indicator_tlc_trend(state_ref.treated_over_24h, state_latest.treated_over_24h, want_increase=False)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'within_4_hrs', aust_latest.treated_within_4h,
                        trend=aust_4h_trend,
                        traffic_light_code=aust_4h_tlc,
                        pval=pval)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'over_24_hrs', aust_latest.treated_over_24h,
                        traffic_light_code=aust_24h_tlc,
                        trend=aust_24h_trend,
                        pval=pval)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'within_4_hrs_state', state_latest.treated_within_4h,
                        trend=state_4h_trend,
                        traffic_light_code=state_4h_tlc,
                        pval=pval)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'over_24_hrs_state', state_latest.treated_over_24h,
                        traffic_light_code=state_24h_tlc,
                        trend=state_24h_trend,
                        pval=pval)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'year_1', state_latest.year_display(),
                        pval=pval)
            set_statistic_data('gpwait-health-hero-state', 'gpwait-health-hero-state',
                        'year_2', state_latest.year_display(),
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'within_4_hrs', aust_latest.treated_within_4h,
                        trend=aust_4h_trend,
                        traffic_light_code=aust_4h_tlc,
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'over_24_hrs', aust_latest.treated_over_24h,
                        traffic_light_code=aust_24h_tlc,
                        trend=aust_24h_trend,
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'within_4_hrs_state', state_latest.treated_within_4h,
                        trend=state_4h_trend,
                        traffic_light_code=state_4h_tlc,
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'over_24_hrs_state', state_latest.treated_over_24h,
                        traffic_light_code=state_24h_tlc,
                        trend=state_24h_trend,
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'year_1', state_latest.year_display(),
                        pval=pval)
            set_statistic_data("health_gpwait_state", "health_gpwait_state",
                        'year_2', state_latest.year_display(),
                        pval=pval)
            messages.extend(
                    update_graph_data(
                            "health_gpwait_state", "health_gpwait_state",
                            "health_gpwait_detail_graph_4hrs",
                            HealthGPWaitData, "treated_within_4h",
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
            messages.extend(
                    update_graph_data(
                            "health_gpwait_state", "health_gpwait_state",
                            "health_gpwait_detail_graph_24hrs",
                            HealthGPWaitData, "treated_over_24h",
                            use_error_bars=False,
                            verbosity=verbosity,
                            pval=pval)
            )
            messages.extend(
                    populate_raw_data("health_gpwait_state", "health_gpwait_state",
                                "health_gpwait", HealthGPWaitData, 
                                {
                                    "treated_within_4h": "percentage_within_4_hrs",
                                    "treated_4_24h": "percentage_4_to_24_hrs",
                                    "treated_over_24h": "percentage_over_24_hrs",
                                },
                                pval=pval)
            )
            messages.extend(
                    populate_crosstab_raw_data("health_gpwait_state", "health_gpwait_state",
                                "data_table", HealthGPWaitData,
                                {
                                    "treated_within_4h": "within_4_hrs",
                                    "treated_4_24h": "4_to_24_hrs",
                                    "treated_over_24h": "over_24_hrs",
                                },
                                pval=pval)
            )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

