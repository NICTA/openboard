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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template import Engine, Context
from django.apps import apps

from widget_def.models.views import WidgetView, ViewProperty
from widget_def.models.widget_decl import ViewWidgetDeclaration

class ParametisationException(Exception):
    pass

@receiver(post_save, sender=WidgetView)
@receiver(post_delete, sender=WidgetView)
@receiver(post_save, sender=ViewWidgetDeclaration)
@receiver(post_delete, sender=ViewWidgetDeclaration)
@receiver(post_save, sender=ViewProperty)
@receiver(post_delete, sender=ViewProperty)
def update_parametisations(sender, instance, **kwargs):
    if sender == WidgetView:
        v = instance
    else:
        v = instance.view
    Parametisation = apps.get_app_config("widget_def").get_model("Parametisation")
    Parametisation.update_all(v)

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
        context = Context(view.properties())
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



