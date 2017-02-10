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

