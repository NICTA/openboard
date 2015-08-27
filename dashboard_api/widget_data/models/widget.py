from django.db import models

# Create your models here.

class WidgetData(models.Model):
    widget = models.OneToOneField("widget_def.WidgetDefinition")
    actual_frequency_text = models.CharField(max_length=60, blank=True, null=True)

