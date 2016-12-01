#   Copyright 2016 CSIRO
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

class EducationEceNqsData(CoagDataBase):
    meeting_nqs = models.DecimalField(max_digits=6, decimal_places=0)
    working_towards = models.DecimalField(max_digits=6, decimal_places=0)
    no_rating = models.DecimalField(max_digits=6, decimal_places=0)
    def total(self):
        return self.meeting_nqs + self.working_towards + self.no_rating
    def meeting_nqs_pct(self):
        return float(self.meeting_nqs)/float(self.total())*100.0
    def working_towards_pct(self):
        return float(self.working_towards)/float(self.total())*100.0
    def no_rating_pct(self):
        return float(self.no_rating)/float(self.total())*100.0

