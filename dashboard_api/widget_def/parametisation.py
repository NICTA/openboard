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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template import Engine, Context
from widget_def.models.parametisation import Parametisation, ParametisationValue, ViewDoesNotHaveAllKeys
from widget_def.models.reference import WidgetView, ViewProperty

@receiver(post_save, sender=WidgetView)
@receiver(post_delete, sender=WidgetView)
@receiver(post_save, sender=ViewProperty)
@receiver(post_delete, sender=ViewProperty)
def update_parametisations(sender, instance, **kwargs):
    if sender == WidgetView:
        v = instance
    else:
        v = instance.view
    Parametisation.update_all(v)


def parametise_label(widget_or_parametisation, view, text):
    if text is None:
        return None
    if widget_or_parametisation:
        if isinstance(widget_or_parametisation, Parametisation):
            param = widget_or_parametisation
        else:
            param = widget_or_parametisation.parametisation
    else:
         param = None
    if param:
        try:
            context = Context(view.parametisationvalue_set.get(param=param).parameters)
        except ParametisationValue.DoesNotExist:
            raise ViewDoesNotHaveAllKeys()
        eng = Engine.get_default()
        template = eng.from_string(text)
        return template.render(context)
    else:
        return text

