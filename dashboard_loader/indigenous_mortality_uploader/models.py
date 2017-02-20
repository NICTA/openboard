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

class IndigenousMortalityData(CoagDataBase):
    indigenous=models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    non_indigenous=models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    variability_lower=models.DecimalField(max_digits=6, decimal_places=1)
    variability_upper=models.DecimalField(max_digits=6, decimal_places=1)
    indigenous_target=models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    non_indigenous_projected=models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    def non_indigenous_csv_display(self):
        if self.non_indigenous:
            return unicode(self.non_indigenous)
        else:
            return "-"
    def tlc(self):
        if self.indigenous < self.variability_lower:
            return "on_track"
        else:
            return "not_on_track"
