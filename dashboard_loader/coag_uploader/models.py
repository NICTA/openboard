from __future__ import unicode_literals


import re
from django.db import models

# Create your models here.

NSW = 1
VIC = 2
QLD = 3
WA  = 4
SA  = 5
TAS = 6
ACT = 7
NT  = 8
AUS = 100

states = [
    (NSW, 'NSW'),
    (VIC, 'Vic'),
    (QLD, 'Qld'),
    (WA, 'WA'),
    (SA, 'SA'),
    (TAS, 'Tas'),
    (ACT, 'ACT'),
    (NT, 'NT'),
    (AUS, 'Australia'),
]

state_dict = dict(states)

state_map = {
    'NSW': NSW,
    'Vic': VIC,
    'Qld': QLD,
    'SA': SA,
    'Tas': TAS,
    'ACT': ACT,
    'NT': NT,
    'Australia': AUS,
    'Aust': AUS,
}

def fy_display(fy_starting):
    return "%d-%02d" % (fy_starting, (fy_starting+1)%100)

def parse_year(y):
    if isinstance(y, int) or isinstance(y, long):
        return y, False
    ybits = re.split(r"[^0-9]+", y)
    if len(ybits) == 1:
        return int(y), False
    elif len(ybits) == 2:
        int(ybits[1])
        return int(ybits[0]), True
    else:
        raise Exception("Invalid year: %s" % y)

def display_float_year(fy):
    y = int(fy)
    if float(y) == fy:
        return unicode(y)
    else:
        return fy_display(y)

class CoagDataBase(models.Model):
    state = models.SmallIntegerField(choices=states)
    year=models.SmallIntegerField()
    financial_year=models.BooleanField()
    def year_display(self):
        if self.financial_year:
            return fy_display(self.year)
        else:
            return unicode(self.year)
    def float_year(self):
        if self.financial_year:
            return float(self.year) + 0.5
        else:
            return float(self.year)
    def state_display(self):
        return state_dict[self.state]
    class Meta:
        abstract = True

class CoagPercentageUncertaintyDataBase(CoagDataBase):
    percentage = models.DecimalField(max_digits=3, 
                        decimal_places=1)
    uncertainty = models.DecimalField(max_digits=3, 
                        decimal_places=1)
    class Meta:
        abstract = True

class HousingRentalStressData(CoagPercentageUncertaintyDataBase):
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class HousingHomelessData(CoagDataBase):
    homeless_persons = models.IntegerField()
    percent_of_national = models.IntegerField()
    rate_per_10k = models.DecimalField(max_digits=6, decimal_places=1)    
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class IndigenousHomeOwnershipData(CoagPercentageUncertaintyDataBase):
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class IndigenousOvercrowdingData(CoagPercentageUncertaintyDataBase):
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class QualificationsData(CoagPercentageUncertaintyDataBase):
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class HigherQualificationsData(CoagDataBase):
    diploma=models.IntegerField()
    adv_diploma=models.IntegerField()
    total=models.IntegerField()
    def save(self, *args, **kwargs):
        self.total = self.diploma + self.adv_diploma
        super(HigherQualificationsData, self).save(*args, **kwargs)
    class Meta:
        unique_together = [
            ("state", "year"),
        ]

class ImprovedVetGraduatesData(CoagPercentageUncertaintyDataBase):
    class Meta:
        unique_together = [
            ("state", "year"),
        ]


