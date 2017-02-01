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

class EducationNaplanData(CoagDataBase):
    year3_lit_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year5_lit_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year7_lit_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year9_lit_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year3_lit_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year5_lit_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year7_lit_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year9_lit_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year3_num_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year5_num_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year7_num_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year9_num_score = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    year3_num_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year5_num_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year7_num_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    year9_num_nms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    year3_lit_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_lit_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_lit_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_lit_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_lit_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_lit_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_lit_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_lit_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_num_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_num_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_num_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_num_score_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_num_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_num_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_num_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_num_nms_uncertainty = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    year3_lit_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_lit_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_lit_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_lit_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_lit_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_lit_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_lit_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_lit_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_num_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_num_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_num_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_num_score_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year3_num_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year5_num_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year7_num_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    year9_num_nms_rse = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

