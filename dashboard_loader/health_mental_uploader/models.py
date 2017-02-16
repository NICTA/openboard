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
from decimal import Decimal

# Create your models here.

PROJ_COMPLETED = 1

project_statuses = [
    (PROJ_COMPLETED, "Completed"),
]

project_status_dict = dict(project_statuses)
project_status_tlc_dict = {
    PROJ_COMPLETED: "achieved",
}

project_map = {
    "Complete": PROJ_COMPLETED, 
    "complete": PROJ_COMPLETED, 
    "Completed": PROJ_COMPLETED, 
    "completed": PROJ_COMPLETED, 
}

class MentalHealthProjects(CoagProgressBase):
    project = models.CharField(max_length=255)
    progress = models.TextField()
    status = models.SmallIntegerField(choices=project_statuses)
    def state_display(self):
        if self.state == AUS:
            return "Commonwealth"
        else:
            return super(MentalHealthProjects, self).state_display()
    def status_display(self):
        return project_status_dict[self.status]
    def status_tlc(self):
        return project_status_tlc_dict[self.status]
    class Meta(CoagDataBase.Meta):
        unique_together = [
            ('state', 'project'),
        ]
        ordering= ('state', 'project')

