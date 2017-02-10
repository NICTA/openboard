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

from django.db import models
from coag_uploader.models import *

# Create your models here.

class IndigenousChildMortalityNationalData(CoagDataBase):
    indigenous=models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    non_indigenous=models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    variability_lower=models.DecimalField(max_digits=5, decimal_places=1)
    variability_upper=models.DecimalField(max_digits=5, decimal_places=1)
    indigenous_target=models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    non_indigenous_projected=models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

class IndigenousChildMortalityStateData(CoagDataBase):
    indigenous=models.DecimalField(max_digits=5, decimal_places=1)
    non_indigenous=models.DecimalField(max_digits=5, decimal_places=1)
    indigenous_deaths=models.IntegerField()
    non_indigenous_deaths=models.IntegerField()
    rate_ratio=models.DecimalField(max_digits=5, decimal_places=1)
    rate_diff=models.DecimalField(max_digits=5, decimal_places=1)

