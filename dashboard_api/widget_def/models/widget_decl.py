from django.db import models

from widget_def.models.reference import Theme, Location, Frequency
from widget_def.models.widget_definition import WidgetDefinition

# Create your models here.

class WidgetDeclaration(models.Model):
    definition = models.ForeignKey(WidgetDefinition)
    theme = models.ForeignKey(Theme)
    frequency = models.ForeignKey(Frequency, limit_choices_to={
                            "display_mode": True
                    })
    location = models.ForeignKey(Location)
    def __unicode__(self):
        return "%s (%s:%s:%s)" % (self.definition.family.name, self.theme.name, self.location.name, self.frequency.name)
    def __getstate__(self):
        return self.definition.__getstate__()
    def export(self):
        return {
            "theme": self.theme.url,
            "frequency": self.frequency.url,
            "location": self.location.url,
        }
    @classmethod
    def import_data(cls, definition, data):
        try:
            decl = WidgetDeclaration.objects.get(definition=definition, 
                            location__url=data["location"],
                            frequency__url=data["frequency"])
        except WidgetDeclaration.DoesNotExist:
            decl = WidgetDeclaration(definition=definition)
            decl.location = Location.objects.get(url=data["location"])
            decl.frequency = Frequency.objects.get(url=data["frequency"])
            decl.theme = Theme.objects.get(url=data["theme"])
            decl.save()
        return decl
    class Meta:
        unique_together = ( ("theme", "location", "frequency", "definition"),)
        ordering = ("theme", "location", "frequency", "definition")

