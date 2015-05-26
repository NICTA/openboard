from django.db import models

# Create your models here.

class IconLibrary(models.Model):
    name=models.SlugField(unique=True)
    def __unicode__(self):
        return self.name
    def __getstate__(self):
        return [ c.__getstate__() for c in self.iconcode_set.all() ]
    def export(self):
        return {
            "library_name": self.name,
            "codes": [ c.export() for c in self.iconcode_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            l = IconLibrary.objects.get(name=data["library_name"])
        except IconLibrary.DoesNotExist:
            l = IconLibrary(name=data["library_name"])
            l.save()
        values = []
        for c in data["codes"]:
            IconCode.import_data(l, c)
            values.append(c["value"])
        for code in l.iconcode_set.all():
            if code.value not in values:
                code.delete()
        return l
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.iconcode_set.all() ])
        return choices

class IconCode(models.Model):
    scale=models.ForeignKey(IconLibrary)
    value=models.SlugField()
    description=models.CharField(max_length=80)
    sort_order=models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    def export(self):
        return {
            "value": self.value,
            "description": self.description,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, library, data):
        try:
            code = IconCode.objects.get(scale=library, value=data["value"])
        except IconCode.DoesNotExist:
            code = IconCode(scale=library, value=data["value"])
        code.description = data["description"]
        code.sort_order = data["sort_order"]
        code.save()
        return code
    def __getstate__(self):
        return {
            "library": self.scale.name,
            "value": self.value,
            "alt_text": self.description
        }
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]
 
class TrafficLightScale(models.Model):
    name=models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name
    def export(self):
        return {
            "scale_name": self.name,
            "codes": [ c.export() for c in self.trafficlightscalecode_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        try:
            l = TrafficLightScale.objects.get(name=data["scale_name"])
        except TrafficLightScale.DoesNotExist:
            l = TrafficLightScale(name=data["scale_name"])
            l.save()
        values = []
        for c in data["codes"]:
            TrafficLightScaleCode.import_data(l, c)
            values.append(c["value"])
        for code in l.trafficlightscalecode_set.all():
            if code.value not in values:
                code.delete()
        return l
    def __getstate__(self):
        return {
            "scale": self.name,
            "codes": [ c.__getstate__() for c in self.trafficlightscalecode_set.all() ]
        }
    def choices(self, allow_null=False):
        if allow_null:
            choices = [ ("", "--"), ]
        else:
            choices = []
        choices.extend([ (c.value, c.value) for c in self.trafficlightscalecode_set.all() ])
        return choices

class TrafficLightScaleCode(models.Model):
    scale = models.ForeignKey(TrafficLightScale)
    value = models.SlugField()
    colour = models.CharField(max_length=50)
    sort_order = models.IntegerField(help_text='"Good" codes should have lower sort order than "Bad" codes.')
    def __unicode__(self):
        return "%s:%s" % (self.scale.name, self.value)
    def export(self):
        return {
            "value": self.value,
            "colour": self.colour,
            "sort_order": self.sort_order
        }
    @classmethod
    def import_data(cls, scale, data):
        try:
            code = TrafficLightScaleCode.objects.get(scale=scale, value=data["value"])
        except TrafficLightScaleCode.DoesNotExist:
            code = TrafficLightScaleCode(scale=scale, value=data["value"])
        code.colour = data["colour"]
        code.sort_order = data["sort_order"]
        code.save()
        return code
    def __getstate__(self):
        return {
            "value": self.value,
            "colour": self.colour
        }
    class Meta:
        unique_together=[ ("scale", "value"), ("scale", "sort_order") ]
        ordering = [ "scale", "sort_order" ]

