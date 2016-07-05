#   Copyright 2016 NICTA
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


import csv
import decimal
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from widget_def.models import Parametisation, ParametisationValue



# These are the names of the groups that have permission to upload data for this uploader.
# If the groups do not exist they are created on registration.
groups = [ "upload_all", "upload_coag" ]

# This describes the file format.  It is used to describe the format by both
# "python manage.py upload_data frontlineservice_uploader" and by the uploader 
# page in the data admin GUI.
file_format = {
    "format": "xlsx",
    "sheets": [
         {
             "name": "Table of Contents",
             "rows": [],
             "cols": [],
             "notes": [ "Not read by uploader", ],
         },
         {
             "name": "1 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "2 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "3 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
         {
             "name": "4 NAHA",
             "rows": [],
             "cols": [],
             "notes": [ "TODO", ],
         },
    ],
}

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    return messages

