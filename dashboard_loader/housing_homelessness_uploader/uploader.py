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
from scipy import stats
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from housing_homelessness_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, hero_widgets, update_graph_data, populate_raw_data
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
                            ('B', 'Row Discriminator ("no.", % or "rate per 10k")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Triplets of rows per year, one for number (no.), one for percentage of national total (%), and one for rate (rate per 10k)'),
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
                            ('Status', 'Benchmark status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of benchmark status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

benchmark = "From 2006 to 2013, a 7% reduction nationally in the number of homeless Australians"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Housing", "Homelessness",
                                None, HousingHomelessData,
                                {}, {
                                    "homeless_persons": "no.", 
                                    "percent_of_national": "%",
                                    "rate_per_10k": "rate per 10k",
                                },
                                verbosity)
                )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, verbosity))
        messages.extend(
                update_graph_data(
                            "homelessness-housing-hero", "homelessness-housing-hero",
                            "housing-hln-hero-graph",
                            HousingHomelessData, "homeless_persons",
                            [ AUS, ],
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: 0.93*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "housing_homelessness", "housing_homelessness",
                            "housing_homelessness_summary_graph",
                            HousingHomelessData, "homeless_persons",
                            [ AUS, ],
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: 0.93*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                update_graph_data(
                            "housing_homelessness", "housing_homelessness",
                            "housing_homelessness_detail_graph",
                            HousingHomelessData, "homeless_persons",
                            benchmark_start=2006,
                            benchmark_end=2013,
                            benchmark_gen=lambda init: 0.93*init,
                            use_error_bars=False,
                            verbosity=verbosity)
                )
        messages.extend(
                populate_raw_data("housing_homelessness", "housing_homelessness",
                            "housing_homelessness", HousingHomelessData,
                            {
                                "homeless_persons": "number_homeless_persons",
                                "percent_of_national": "proportion_national_total",
                                "rate_per_10k": "rate_per_10k",
                            })
                )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

txt_block_template = Template("""<div class="coag_description">
    <div class="coag_desc_heading">
    {{ benchmark }}
    </div>
    <div class="coag_desc_body">
        {% for body_elem in desc.body %}
            <p>{{ body_elem }}</p>
        {% endfor %}
        {% for inf_elem in desc.influences %}
            <p>
                {% if forloop.first %}
                    <b>Influences:</b>
                {% endif %}
                {{ inf_elem }}
            </p>
        {% endfor %}
    </div>
    <div class="coag_desc_notes">'
        <p>Notes:</p>
        <ol>
            {% for note in desc.notes %}
                <li>{{ note }}</li>
            {% endfor %}
        </ol>
    </div>
</div>""")

def update_stats(desc, verbosity):
    messages = []
    for w in hero_widgets["housing"]:
        set_statistic_data(w, w, "homelessness", None, 
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
    set_statistic_data("homelessness-housing-hero", "homelessness-housing-hero", 
                    "summary",
                    benchmark,
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
    set_statistic_data("housing_homelessness", "housing_homelessness", 
                    "summary",
                    benchmark,
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
    set_statistic_data("housing_homelessness", "housing_homelessness", 
                    "status_short",
                    desc["status"]["short"],
                    traffic_light_code=desc["status"]["tlc"],
                    icon_code=desc["status"]["icon"])
    set_statistic_data("housing_homelessness", "housing_homelessness", 
                    "status_long",
                    desc["status"]["long"],
                    traffic_light_code=desc["status"]["tlc"])
    set_actual_frequency_display_text("housing_homelessness", "housing_homelessness",
                "Updated: %s" % unicode(desc["updated"]))
    set_text_block("housing_homelessness", "housing_homelessness",
                txt_block_template.render(Context({ 
                                "benchmark": benchmark, 
                                "desc": desc })))
    if verbosity > 1:
        messages.append("Stats updated")
    return messages

