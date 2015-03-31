from django.db import models

# Create your models here.

class MajorIncident(models.Model):
    text = models.CharField(max_length=255)
    last_featured = models.DateTimeField()

