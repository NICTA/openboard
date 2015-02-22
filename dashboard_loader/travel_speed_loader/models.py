from django.db import models

# Create your models here.

class Road(models.Model):
    name = models.CharField(max_length=5, unique=True)
    am_direction=models.CharField(max_length=1)
    pm_direction=models.CharField(max_length=1)
    def __unicode__(self):
        return self.name

class RoadSection(models.Model):
    road = models.ForeignKey(Road)
    label = models.CharField(max_length=10)
    origin = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    direction = models.CharField(max_length=20)
    route_direction = models.CharField(max_length=1)
    length = models.IntegerField(null=True, blank=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.road.name, self.label)
    def save(self, *args, **kwargs):
        direction = self.label[0]
        remainder = self.label[1:]
        if direction == "N":
            base = 100
        elif direction == "S":
            base = 200
        elif direction == "W":
            base = 300
        else:
            base = 400
        if remainder == "TOTAL":
            index = 99
        else:
            index = int(remainder)
        self.sort_order = base + index
        super(RoadSection, self).save(*args, **kwargs)
    class Meta:
        unique_together = ( ('road', 'sort_order'), ('road', 'label'), ('road', 'origin', 'destination') )
        ordering = ('road', 'sort_order')


