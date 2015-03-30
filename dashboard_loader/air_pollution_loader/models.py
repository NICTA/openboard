from django.db import models

from widget_def.models import Location

# Create your models here.

class PollutionRotation(models.Model):
    location = models.ForeignKey(Location)
    region = models.CharField(max_length=80)
    last_featured = models.DateTimeField()
    class Meta:
        unique_together=[ ("location", "region") ]

