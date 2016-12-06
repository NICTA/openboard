from __future__ import unicode_literals

from django.db import models
from coag_uploader.models import *

# Create your models here.

class IndigenousChildMortalityNationalData(CoagDataBase):
    indigenous=models.DecimalField(max_digits=5, decimal_places=1)
    non_indigenous=models.DecimalField(max_digits=5, decimal_places=1)

class IndigenousChildMortalityStateData(CoagDataBase):
    indigenous=models.DecimalField(max_digits=5, decimal_places=1)
    non_indigenous=models.DecimalField(max_digits=5, decimal_places=1)
    def gap(self):
        return self.nonindigenous - self.indigenous

