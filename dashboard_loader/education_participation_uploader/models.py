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

class EducationParticipationData(CoagDataBase):
    study = models.DecimalField(max_digits=4, decimal_places=1)
    work = models.DecimalField(max_digits=4, decimal_places=1)
    study_work = models.DecimalField(max_digits=4, decimal_places=1)
    not_engaged = models.DecimalField(max_digits=4, decimal_places=1)
    def engaged(self):
        return self.study + self.work + self.study_work
