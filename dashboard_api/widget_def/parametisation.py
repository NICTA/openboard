#   Copyright 2016,2017 CSIRO
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

from django.template import Engine, Context
from django.apps import apps

class ParametisationException(Exception):
    pass

def parametise_label(widget_or_parametisation, view, text):
    if text is None:
        return None
    Parametisation = apps.get_app_config("widget_def").get_model("Parametisation")
    if widget_or_parametisation:
        if isinstance(widget_or_parametisation, Parametisation):
            param = widget_or_parametisation
        else:
            param = widget_or_parametisation.parametisation
    else:
         param = None
    if param:
        context = Context(view.my_properties())
        eng = Engine.get_default()
        template = eng.from_string(text)
        return template.render(context)
    else:
        return text

def resolve_pval(parametisation, view=None, pval=None):
    if parametisation:
        if view:
            pval = view.parametisationvalue_set.get(param=parametisation)
        elif not pval:
            raise ParametisationException("Cannot resolve parametisation")
        return pval
    else:
        return None



