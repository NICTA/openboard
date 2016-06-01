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

from django.db import models

# Create your models here.

class Parametisation(models.Model):
    url=models.SlugField(unique=True)
    name=models.CharField(max_length=128, unique=True)
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)
    def export(self):
        return {
            "url": self.url,
            "name": self.name,
            "keys": [ pk.key for pk in self.parametisationkeys_set.all() ],
        }
    def add_key(self, key):
        return ParametisationKey.objects.get_or_create(param=self, key=key)
    def delete_key(self, key):
        try:
            ParametisationKey.objects.get(param=self, key=key).delete()
        except ParametisationKey.DoesNotExist:
            pass
    def keys(self):
        return [ pk.key for pk in self.parametisationkey_set.all() ]
    @classmethod
    def import_data(cls, data):
        p = cls.objects.get_or_create(url=data["url"], name=data["name"])
        for k in data["keys"]:
            p.add_key(k)
        for k in self.keys():
            if k not in data["keys"]:
                p.delete_key(k)
        return p
    class Meta:
        ordering = ("name",)

class ParametisationKey(models.Model):
    param = models.ForeignKey(Parametisation)
    key = models.CharField(max_length=120)
    def __unicode__(self):
        return "%s[%s]" % (self.param.name, self.key)
    class Meta:
        unique_together=[("param", "key"),]
        ordering=("param", "key")

