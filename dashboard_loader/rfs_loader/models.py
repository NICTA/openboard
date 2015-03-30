from django.db import models

# Create your models here.

class CurrentRating(models.Model):
    region = models.CharField(max_length=50, unique=True)
    rating = models.IntegerField()
    rating_text = models.CharField(max_length=50)
    tlc = models.CharField(max_length=50)
    last_featured = models.DateTimeField(blank=True, null=True)


