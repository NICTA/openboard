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


import datetime
import csv
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from health_life_expectancy_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, indicator_tlc_trend

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
                            ('B', 'Row Discriminator ("Males" or "Females")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for men (Males) and one for women (Females)'),
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

indicators = "Improve life expectancy for Australian men and women"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Health", "Life Expectancy",
                                None, HealthLifeExpectancyData,
                                {}, {"males": "Males", "females": "Females",},
                                verbosity, multi_year=True))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicators,
                                "life_expectancy-health-hero", "life_expectancy-health-hero", 
                                None, None,
                                verbosity))
        earliest_aust = HealthLifeExpectancyData.objects.filter(state=AUS).order_by("year").first()
        latest_aust = HealthLifeExpectancyData.objects.filter(state=AUS).order_by("year").last()
        male_tlc, male_trend = indicator_tlc_trend(earliest_aust.males, latest_aust.males)
        female_tlc, female_trend = indicator_tlc_trend(earliest_aust.females, latest_aust.females)

        set_statistic_data('life_expectancy-health-hero', 'life_expectancy-health-hero',
                        'men_life_exp',
                        latest_aust.males,
                        traffic_light_code=male_tlc,
                        trend=male_trend)
        set_statistic_data('life_expectancy-health-hero', 'life_expectancy-health-hero',
                        'women_life_exp',
                        latest_aust.females,
                        traffic_light_code=female_tlc,
                        trend=female_trend)
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

