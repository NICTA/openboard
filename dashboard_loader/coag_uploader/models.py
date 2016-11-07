from __future__ import unicode_literals


import re
from datetime import date
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
    'VIC': VIC,
    'Qld': QLD,
    'QLD': QLD,
    'WA': WA,
    'SA': SA,
    'Tas': TAS,
    'TAS': TAS,
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

def parse_multiyear(y):
    if isinstance(y, int) or isinstance(y, long):
        return y, 1
    ybits = re.split(r"[^0-9]+", y)
    if len(ybits) == 1:
        return int(y), 1
    elif len(ybits) == 2:
        a = int(ybits[0])
        b = int(ybits[1])
        if a > b:
            b = b + (a - a%100)
            if b - a < 0:
                b += 100
        return a, (b-a)+1
    else:
        raise Exception("Invalid year: %s" % y)

def display_float_year(fy):
    y = int(fy)
    if float(y) == fy:
        return unicode(y)
    else:
        return fy_display(y)

def float_year_as_date(fy):
    iy = int(fy)
    if float(iy) == fy:
        return date(iy, 1, 1)
    else:
        return date(iy, 7, 1)

class CoagDataBase(models.Model):
    state = models.SmallIntegerField(choices=states)
    year=models.SmallIntegerField()
    financial_year=models.BooleanField()
    multi_year=models.IntegerField(default=1)
    def year_display(self):
        if self.financial_year:
            return fy_display(self.year)
        elif self.multi_year > 1:
            return "%04d-%02d" % (self.year, (self.year+self.multi_year-1)%100)
        else:
            return unicode(self.year)
    def float_year(self):
        if self.financial_year:
            return float(self.year) + 0.5
        elif self.multi_year > 1:
            return float(self.year + self.multi_year - 1)
        else:
            return float(self.year)
    def year_as_date(self):
        if self.financial_year:
            return date(self.year, 7, 1)
        elif self.multi_year > 1:
            return date(self.year + self.multi_year - 1, 1, 1)
        else:
            return date(self.year, 1, 1)
    def state_display(self):
        return state_dict[self.state]
    def save(self, *args, **kwargs):
        if self.financial_year and self.multi_year > 1:
            raise Exception("COAG datapoint cannot cover multiple financial years")
        return super(CoagDataBase, self).save(*args, **kwargs)
    class Meta:
        unique_together = [ ("state", "year"), ]
        abstract = True

class CoagPercentageUncertaintyDataBase(CoagDataBase):
    percentage = models.DecimalField(max_digits=3, 
                        decimal_places=1)
    uncertainty = models.DecimalField(max_digits=3, 
                        decimal_places=1)
    class Meta(CoagDataBase.Meta):
        abstract = True

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


