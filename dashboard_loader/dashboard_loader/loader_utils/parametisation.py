#   Copyright 2016 NICTA
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

from interface import LoaderException
from widget_def.models import Parametisation, ViewDoesNotHaveAllKeys

def get_paramval(parametisation, **kwargs):
    if isinstance(parametisation, Parametisation):
        param = parametisation
    else:
        param = Parametisation.objects.get(url=parametisation)
    try:
        for pval in param.parametisationvalue_set.all():
            if pval.matches_parameters(kwargs):
                return pval
    except ViewDoesNotHaveAllKeys:
        LoaderException("Parametisation error. Insuffient parameter specification for %s: %s" % 
                                (param.url, repr(kwargs)))
    raise LoaderException("Parametisation %s has no value set that matches %s" % 
                                (param.url, repr(kwargs)))

