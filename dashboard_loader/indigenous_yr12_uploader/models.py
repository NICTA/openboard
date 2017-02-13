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

from __future__ import unicode_literals

from django.db import models
from coag_uploader.models import *

# Create your models here.

class IndigenousYr12Data(CoagDataBase):
    indigenous_attainment=models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    indigenous_trajectory=models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    def benchmark_tlc(self, complete=False):
        if self.indigenous_trajectory > self.indigenous_attainment:
            if complete:
                return "not_met"
            else:
                return "not_on_track"
        else:
            if complete:
                return "achieved"
            else:
                return "on_track"

