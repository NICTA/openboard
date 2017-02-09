#   Copyright 2016,2017 CSIRO
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

from __future__ import unicode_literals

import datetime
from django.db import models
from coag_uploader.models import *

# Create your models here.

class LegalAssistData(CoagDateDataBase):
    lac=models.DecimalField(max_digits=4, decimal_places=1)
    clc=models.DecimalField(max_digits=4, decimal_places=1)
    lac_benchmark=models.DecimalField(max_digits=4, decimal_places=1)
    clc_benchmark=models.DecimalField(max_digits=4, decimal_places=1)
    def meets_lac_benchmark(self):
        return self.lac >= self.lac_benchmark
    def meets_clc_benchmark(self):
        return self.clc >= self.clc_benchmark
    def tlc_lac(self):
        if self.meets_lac_benchmark:
            return "achieved"
        else:
            return "not_met"
    def tlc_clc(self):
        if self.meets_clc_benchmark:
            return "achieved"
        else:
            return "not_met"
    def tlc_overall(self):
        lac = self.tlc_lac()
        clc = self.tlc_clc()
        if lac == clc:
            return lac
        else:
            return "mixed_results"
    def end_date(self):
        month = (self.start_date.month + 5) % 12 + 1
        if self.start_date.month >= 7:
            year = self.start_date.year + 1
        else:
            year = self.start_date.year
        return datetime.date(year, month, 1) - datetime.timedelta(days=1)
    def format_date(self, d):
        return d.strftime("%Y-%m")
    def format_daterange_pretty(self):
        return "%s to %s" % (self.start_date.strftime("%B"),
                            self.end_date().strftime("%B %Y"))

