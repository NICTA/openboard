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

READING = 1
NUMERACY = 2

subject_choices = (
    (READING, "Reading"),
    (NUMERACY, "Numeracy"),
)

subject_dict = dict(subject_choices)

subject_map = {
    "READING": READING,
    "Reading": READING,
    "reading": READING,
    "LITERACY": READING,
    "Literacy": READING,
    "literacy": READING,
    "NUMERACY": NUMERACY,
    "Numeracy": NUMERACY,
    "numeracy": NUMERACY,
}

class IndigenousNaplanData(CoagProgressBase):
    year_lvl=models.IntegerField()
    subject=models.SmallIntegerField(choices=subject_choices)
    indig_proportion_above_nms=models.DecimalField(max_digits=5, decimal_places=1)
    indig_confidence_interval=models.DecimalField(max_digits=5, decimal_places=1)
    indig_trajectory=models.DecimalField(max_digits=5, decimal_places=1)
    def on_track(self):
        return self.indig_proportion_above_nms + self.indig_confidence_interval >= self.indig_trajectory
    def tlc(self):
        if self.on_track():
            return "on_track"
        else:
            return "not_on_track"
    class Meta(CoagProgressBase.Meta):
        unique_together=[
            ('state', 'subject', 'year_lvl'),
        ]
        ordering = ("state", "subject", "year_lvl")
        abstract = False
