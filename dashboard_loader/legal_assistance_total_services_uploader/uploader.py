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
from legal_assistance_total_services_uploader.models import *
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
                            ('A', 'Year or financial year e.g. 2007/08, 2007-08 or 2007'),
                            ('B', 'Row Discriminator (Must be "Total services delivered")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'One row per year for total services delivered'),
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
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line. (optional)'),
                            ('Notes', 'Notes for indicator status description.  One note per line.'),
                            ('Vic, NSW, Qld, etc.', 'State-specific comments. One paragraph per line. (optional)'),
                        ],
                "notes": [
                         ],
            }
        ],
}

benchmark = "25% increase in the total number of services delivered by legal aid commissions by 30 June 2015"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Legal Assistance", "Total Services",
                                None, LegalAssistTotalServices,
                                {}, {"total_svcs_delivered": "Total services delivered",},
                                verbosity))
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, benchmark,
                                "total_svc-legal-hero", "total_svc-legal-hero", 
                                "total_svc-legal-hero-state", "total_svc-legal-hero-state", 
                                None,None,
                                None,None,
                                verbosity))
        earliest_aust = LegalAssistTotalServices.objects.filter(state=AUS).order_by("year").first()
        latest_aust = LegalAssistTotalServices.objects.filter(state=AUS).order_by("year").last()
        aust_change, aust_tlc, aust_trend = change_tlc_trend(earliest_aust.total_svcs_delivered, latest_aust.total_svcs_delivered)
        set_statistic_data("total_svc-legal-hero", "total_svc-legal-hero",
                        "benchmark", 25.0, traffic_light_code="achieved")
        set_statistic_data("total_svc-legal-hero", "total_svc-legal-hero",
                        "achievement", aust_change, traffic_light_code=aust_tlc,
                        trend=aust_trend)
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            earliest_state = LegalAssistTotalServices.objects.filter(state=state_num).order_by("year").first()
            latest_state = LegalAssistTotalServices.objects.filter(state=state_num).order_by("year").last()
            state_change, state_tlc, state_trend = change_tlc_trend(earliest_state.total_svcs_delivered, latest_state.total_svcs_delivered)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "benchmark", 25.0, traffic_light_code="achieved", 
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "achievement", aust_change, traffic_light_code=aust_tlc,
                        trend=aust_trend, 
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "benchmark_state", 25.0, traffic_light_code="achieved", 
                        pval=pval)
            set_statistic_data("total_svc-legal-hero-state", "total_svc-legal-hero-state",
                        "achievement_state", state_change, traffic_light_code=state_tlc,
                        trend=state_trend, 
                        pval=pval)
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def change_tlc_trend(ref, end):
    diff = end-ref
    trend = diff / abs(diff)
    change = float(diff)/float(end)
    if change >= 25.0:
        tlc = "achieved"
    else:
        tlc = "not_met"
    return abs(change), tlc, trend

