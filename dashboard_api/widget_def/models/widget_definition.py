#   Copyright 2015,2016 NICTA
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
from django.apps import apps

from widget_data.models import WidgetData, StatisticData, StatisticListItem, GraphData

from widget_def.models.parametisation import Parametisation
from widget_def.view_utils import max_with_nulls
from widget_def.parametisation import parametise_label, resolve_pval, ParametisationException

# Create your models here.

class WidgetDefinition(models.Model):
    _lud_cache = None
    family = models.ForeignKey("WidgetFamily")
    parametisation = models.ForeignKey(Parametisation, blank=True, null=True)
    expansion_hint = models.CharField(max_length=80, blank=True, null=True)
    deexpansion_hint = models.CharField(max_length=80, blank=True, null=True)
    label = models.CharField(max_length=128)
    default_frequency_text = models.CharField(max_length=60)
    refresh_rate = models.IntegerField(help_text="in seconds")
    sort_order = models.IntegerField(unique=True)
    about = models.TextField(null=True, blank=True)
    def validate(self):
        """Validate Widget Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        if self.parametisation:
            if self.family.widgetdefinition_set.exclude(id=self.id).count() > 0:
                problems.append("Parametised widget %s:%s is not only widget defintion in family" % (self.url(),self.label))
        else:
            if self.family.widgetdefinition_set.filter(parametisation__isnull=False).count() > 0:
                problems.append("Non-parametised widget %s:%s has a paremetised widget defintion in the same family" % (self.url(),self.label))
        if not self.about:
            problems.append("Widget %s:%s has no 'about' information" % (self.url(), self.label))
        if self.viewwidgetdeclaration_set.all().count() == 0:
            problems.append("Widget %s:%s has no declarations" % (self.url(), self.label))
        default_tiles = self.tiledefinition_set.filter(expansion=False).count()
        if default_tiles < 1:
            problems.append("Widget %s:%s has no default (non-expansion) tiles - must have at least one" % (self.url(), self.label))
        tiles = self.tiledefinition_set.all()
        if tiles.count() == default_tiles:
            if self.expansion_hint or self.deexpansion_hint:
                problems.append("widget %s:%s has no expansion tiles but expansion hint or deexpansion hint is set" % (self.url(), self.label))
        else:
            if not self.expansion_hint or not self.deexpansion_hint:
                problems.append("widget %s:%s has expansion tiles but expansion hint is not set" % (self.url(), self.label))
        stat_urls = {}
        Statistic = apps.get_app_config("widget_def").get_model("Statistic")
        for stat in Statistic.objects.filter(tile__widget=self):
            if stat.url in stat_urls:
                problems.append("Widget %s:%s has two statistics with url '%s' (in tiles %s and %s)" % (self.url(), self.label, stat.url, stat.tile.url, stat_urls[stat.url]))
            else:
                stat_urls[stat.url] = stat.tile.url
        text_block_tiles = 0
        for tile in tiles:
            problems.extend(tile.validate())
            if tile.tile_type == tile.TEXT_BLOCK:
                text_block_tiles += 1
        if text_block_tiles > 1:
            problems.append("Widget %s:%s has two TEXT BLOCK tiles" % (self.url(), self.label))
        return problems
    def subcategory(self):
        return self.family.subcategory
    def url(self):
        return self.family.url
    def name(self):
        return self.family.name
    def subtitle(self):
        return self.family.subtitle
    def source_url(self):
        return self.family.source_url
    def widget_data(self, view=None, pval=None):
        try:
            pval = resolve_pval(self.parametisation, view=view, pval=pval)
        except ParametisationException:
            pval = None
        if pval:
            try:
                return WidgetData.objects.get(widget=self, param_value=pval)
            except WidgetData.DoesNotExist:
                pass
        try:
            return WidgetData.objects.get(widget=self, param_value=pval)
        except WidgetData.DoesNotExist:
            return None
    def actual_frequency_display(self, wd=None, view=None, pval=None):
        if not wd:
            wd = self.widget_data(view, pval)
        if wd and wd.actual_frequency_text:
            return wd.actual_frequency_text
        else:
            return self.default_frequency_text
    def __getstate__(self, view=None):
        if not self.parametisation:
            view = None
        data = {
            "category": self.subcategory().category.name,
            "category_aspect": self.subcategory().category.category_aspect,
            "subcategory": self.subcategory().name,
            "name": parametise_label(self, view, self.name()),
            "subtitle": parametise_label(self, view, self.family.subtitle),
            "label": self.url(),
            "display": {
                "expansion_hint": self.expansion_hint,
                "deexpansion_hint": self.deexpansion_hint,
                "tiles": [ tile.__getstate__(view) for tile in self.tiledefinition_set.all() ],
            },
            "source_url": parametise_label(self, view, self.source_url()),
            "source_url_text": parametise_label(self, view, self.family.source_url_text),
            "refresh_rate": self.refresh_rate,
            "about": parametise_label(self, view, self.about),
        }
        if self.rawdataset_set.all().count() > 0:
            data["raw_data_sets"] = [ rds.__getstate__() for rds in self.rawdataset_set.all() ]
        return data
    def export(self):
        data = {
            "expansion_hint": self.expansion_hint,
            "deexpansion_hint": self.deexpansion_hint,
            "refresh_rate": self.refresh_rate,
            "sort_order": self.sort_order,
            "label": self.label,
            "default_frequency_text": self.default_frequency_text,
            "about": self.about,
            "tiles": [ t.export() for t in self.tiledefinition_set.all() ],
            "views": [ vwd.export() for vwd in self.viewwidgetdeclaration_set.all() ],
            "raw_data_sets": [ rds.export() for rds in self.rawdataset_set.all() ],
        }
        if self.parametisation:
            data["parametisation"] = self.parametisation.url
        else:
            data["parametisation"] = None
        return data
    @classmethod
    def import_data(cls, family, data):
        try:
            w = WidgetDefinition.objects.get(family=family, label=data["label"])
        except WidgetDefinition.DoesNotExist:
            w = WidgetDefinition(family=family, label=data["label"])
        w.expansion_hint = data["expansion_hint"]
        w.deexpansion_hint = data.get("deexpansion_hint")
        w.label = data["label"]
        w.default_frequency_text = data["default_frequency_text"]
        w.refresh_rate = data["refresh_rate"]
        w.sort_order = data["sort_order"]
        w.about = data["about"]
        if data.get("parametisation"):
            w.parametisation = Parametisation.objects.get(url=data["parametisation"])
        else:
            w.parametisation = None
        w.save()
        tile_urls = []
        TileDefinition = apps.get_app_config("widget_def").get_model("TileDefinition")
        for t in data["tiles"]:
            TileDefinition.import_data(w, t)
            tile_urls.append(t["url"])
        for tile in w.tiledefinition_set.all():
            if tile.url not in tile_urls:
                tile.delete()
        if "declarations" in data:
            print "WARNING: Old-style widget declarations ignored."
        ViewWidgetDeclaration = apps.get_app_config("widget_def").get_model("ViewWidgetDeclaration")
        for v in data["views"]:
            vwd = ViewWidgetDeclaration.import_data(w, v)
        for vwd in w.viewwidgetdeclaration_set.all():
            found = False
            for v in data["views"]:
                if vwd.view.label == v["view"]:
                    found = True
                    break
            if not found:
                vwd.delete()
        rds_urls = []
        RawDataSet = apps.get_app_config("widget_def").get_model("RawDataSet")
        for ds in data.get("raw_data_sets", []):
            rds = RawDataSet.import_data(w, ds)
            rds_urls.append(rds.url)
        for rds in RawDataSet.objects.filter(widget=w):
            if rds.url not in rds_urls:
                rds.delete()
        return w
    def __unicode__(self):
        return "%s (%s)" % (unicode(self.family), self.label)
    def data_last_updated(self, update=False, view=None, pval=None):
        pval = resolve_pval(self.parametisation, view=view, pval=pval)
        if pval:
            if self._lud_cache and self._lud_cache.get(pval.id) and not update:
                return self._lud_cache[pval.id]
            if not self._lud_cache:
                self._lud_cache = {}
            latest = None
            Statistic = apps.get_app_config("widget_def").get_model("Statistic")
            for s in Statistic.objects.filter(tile__widget=self):
                slu = s.data_last_updated(update, view, pval)
                if latest is None:
                    latest = slu
                elif slu and slu > latest:
                    latest = slu
            self._lud_cache[pval.id] = latest
            return self._lud_cache[pval.id]
        else:
            if self._lud_cache and not update:
                return self._lud_cache
            lud_statdata = StatisticData.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
            lud_listdata = StatisticListItem.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
            lud_graphdata = GraphData.objects.filter(graph__tile__widget=self).aggregate(lud=models.Max("last_updated"))["lud"]
            luds_mapdata = [None]
            for t in self.tiledefinition_set.all():
                for ds in t.geo_datasets.all():
                    luds_mapdata.append(ds.data_last_updated(update))
            self._lud_cache = max_with_nulls(lud_statdata, lud_listdata, lud_graphdata, *luds_mapdata)
            return self._lud_cache
    class Meta:
        unique_together = (
            ("family", "label"),
        )
        ordering = ("family__subcategory", "sort_order")

