#   Copyright 2017 CSIRO
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

from django.db import models

# Create your models here.

class PropertyGroup(models.Model):
    name = models.CharField(max_length=80, help_text="Descriptive name of the Property Group", unique=True)
    label = models.SlugField(help_text="Short symbolic name of the Property Group, as used in API", unique=True)
    def __unicode__(self):
        return "%s[%s]" % (self.name, self.label)
    def export(self):
        return {
            "name": self.name,
            "label": self.label,
            "properties": [ { "key": p.key, "value": p.value } for p in self.property_set.all() ]
        }
    @classmethod
    def import_data(cls, data):
        if data.get("type"):
            output = []
            for pg in data["exports"]:
                output.append(cls.import_data(pg))
            return output
        try:
            pg = cls.objects.get(label=data["label"])
        except cls.DoesNotExist:
            pg = cls(label=data["label"])
        pg.name = data["name"]
        pg.save()
        pg.property_set.all().delete()
        for pd in data["properties"]:
            Property.import_data(pg, pd)
        return pg
    def __getstate__(self):
        return {
            "name": self.name,
            "label": self.label,
            "properties": { p.key: p.value for p in self.property_set.all() }
        }
    def getindex(self):
        return {
            "name": self.name,
            "label": self.label,
        }

class Property(models.Model):
    group = models.ForeignKey(PropertyGroup, help_text="The group this property belongs to")
    key = models.CharField(max_length=255, help_text="The key (lookup value) of this property")
    value = models.CharField(max_length=1024, help_text="The value (mapped value) of this property")
    def __unicode__(self):
        return '(%s) "%s": "%s"' % (self.group.label, self.key, self.value)
    def export(self):
        return {
            "key": self.key,
            "value": self.value
        }
    @classmethod
    def import_data(cls, grp, data):
        try:
            p = cls.objects.get(group=grp, key=data["key"])
        except cls.DoesNotExist:
            p = cls(group=grp, key=data["key"])
        p.value = data["value"]
        p.save()
        return p
    class Meta:
        unique_together = [ ('group', 'key'), ]
        ordering = [ 'group', 'key' ]
        verbose_name_plural = "properties"

