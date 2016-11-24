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

class InfrastructureProjectCounts(CoagDataBase):
    completed = models.DecimalField(max_digits=4, decimal_places=0)
    underway = models.DecimalField(max_digits=4, decimal_places=0)
    pending = models.DecimalField(max_digits=4, decimal_places=0)

class InfrastructureProjectFundingProportion(CoagDataBase):
    completed = models.DecimalField(max_digits=4, decimal_places=1)
    underway = models.DecimalField(max_digits=4, decimal_places=1)
    pending = models.DecimalField(max_digits=4, decimal_places=1)

PROJ_COMPLETED = 1
PROJ_IN_PROGRESS = 2
PROJ_NOT_DUE_TO_COMMENCE = 3
PROJ_NOT_COMPLETED_AND_OVERDUE = 4
PROJ_NA = 5

project_statuses = [
    (PROJ_COMPLETED, "Completed"),
    (PROJ_IN_PROGRESS, "In progress"),
    (PROJ_NOT_DUE_TO_COMMENCE, "Not due to commence"),
    (PROJ_NOT_COMPLETED_AND_OVERDUE, "Not completed and past agreed timeframe"),
    (PROJ_NA, "Not applicable"),
]

project_status_dict = dict(project_statuses)
project_status_tlc_dict = {
    PROJ_COMPLETED: "completed",
    PROJ_IN_PROGRESS: "in_progress",
    PROJ_NOT_DUE_TO_COMMENCE: "not_due_to_commence",
    PROJ_NOT_COMPLETED_AND_OVERDUE: "not_completed_overdue",
    PROJ_NA: "not_applicable",
}

project_map = {
    "Completed": PROJ_COMPLETED, 
    "completed": PROJ_COMPLETED, 
    "In progress": PROJ_IN_PROGRESS, 
    "in progress": PROJ_IN_PROGRESS, 
    "Not due to commence": PROJ_NOT_DUE_TO_COMMENCE, 
    "not due to commence": PROJ_NOT_DUE_TO_COMMENCE, 
    "Not completed and past agreed timeframe": PROJ_NOT_COMPLETED_AND_OVERDUE, 
    "not completed and past agreed timeframe": PROJ_NOT_COMPLETED_AND_OVERDUE, 
    "Overdue": PROJ_NOT_COMPLETED_AND_OVERDUE, 
    "overdue": PROJ_NOT_COMPLETED_AND_OVERDUE, 
    "Not applicable": PROJ_NA, 
    "not applicable": PROJ_NA, 
    "N/A": PROJ_NA, 
    "n/a": PROJ_NA, 
}

class InfrastructureKeyProjectData(CoagDataBase):
    project = models.CharField(max_length=255)
    milestones = models.TextField()
    status = models.SmallIntegerField(choices=project_statuses)
    def status_display(self):
        return project_status_dict[self.status]
    def status_tlc(self):
        return project_status_tlc_dict[self.status]
    class Meta(CoagDataBase.Meta):
        unique_together = [
            ('state', 'year', 'project'),
        ]

