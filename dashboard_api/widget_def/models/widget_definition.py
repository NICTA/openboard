#   Copyright 2015,2016,2017 CSIRO
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
from widget_def.view_tools import max_with_nulls
from widget_def.parametisation import parametise_label, resolve_pval, ParametisationException
from widget_def.model_json_tools import *


# Create your models here.

class WidgetDefinition(models.Model, WidgetDefJsonMixin):
    """
    Represents a widget.

    Widgets may appear in multiple views. When closely related but distinct widgets appear in different views,
    this can be accomplished either by parametisation or by grouping widgets into a family.
    """
    export_def = {
        "family": JSON_INHERITED("definitions"),
        "parametisation": JSON_CAT_LOOKUP(["parametisation", "url"], lambda js, key, imp_kwargs: Parametisation.objects.get(url=js["parametisation"])),
        "expansion_hint": JSON_ATTR(),
        "deexpansion_hint": JSON_ATTR(),
        "refresh_rate": JSON_ATTR(),
        "label": JSON_ATTR(),
        "default_frequency_text": JSON_ATTR(),
        "about": JSON_ATTR(),
        "sort_order": JSON_IMPLIED(),
        "tiles": JSON_RECURSEDOWN("TileDefinition", "tiles", "widget", "url", app="widget_def"),
        "views": JSON_RECURSEDOWN("ViewWidgetDeclaration", "views", "definition", "view", app="widget_def"),
        "raw_data_sets": JSON_RECURSEDOWN("RawDataSet", "raw_datasets", "widget", "url", app="widget_def")
    }
    export_lookup = { "family": "family", "label": "label" }
    api_state_def = {
        "category": JSON_CAT_LOOKUP(["subcategory", "category", "name"], None),
        "subcategory": JSON_CAT_LOOKUP(["subcategory", "name"], None),
        "category_aspect": JSON_CAT_LOOKUP(["subcategory", "category", "category_aspect"], None),
        "name": JSON_ATTR(parametise=True),
        "subtitle": JSON_ATTR(parametise=True),
        "label": JSON_ATTR(attribute="url"),
        "about": JSON_ATTR(parametise=True),
        "display": JSON_EXP_SUB_DICT({
                    "expansion_hint": JSON_ATTR(),
                    "deexpansion_hint": JSON_ATTR(),
                    "tiles": JSON_RECURSEDOWN("TileDefinition", "tiles", "widget", "url", app="widget_def"),
                }),
        "raw_data_sets": JSON_RECURSEDOWN("RawDataSet", "raw_datasets", "widget", "url", app="widget_def", suppress_if_empty=True)
    }
    _lud_cache = None
    family = models.ForeignKey("WidgetFamily", related_name="definitions", help_text="The widget family")
    parametisation = models.ForeignKey(Parametisation, blank=True, null=True, help_text="The Parametisation. Note that a Parametisation can only be set on a widget definition that is the only widget definition for it's widget family")
    expansion_hint = models.CharField(max_length=80, blank=True, null=True, help_text="The text hint on the control to open expansion tiles. Required for widgets with expansion tiles.")
    deexpansion_hint = models.CharField(max_length=80, blank=True, null=True, help_text="The text hint on the control to close expansion tiles. Required for widgets with expansion tiles.")
    label = models.CharField(max_length=128, help_text="Used in admin interfaces to distinguish between widgets within a family. Not exposed in the API.")
    default_frequency_text = models.CharField(max_length=60, help_text="The default text indicating update frequency or time of last update.  Rarely seen - usually overridden at dataload time.")
    refresh_rate = models.IntegerField(help_text="How often (in seconds) the client should poll Openboard for new data.")
    sort_order = models.IntegerField(unique=True, help_text="How the widget is sorted in admin backend")
    about = models.TextField(null=True, blank=True, help_text="Arbitrary html block describing the widget. May be parametised.")
    def widget(self):
        return self
    def validate(self):
        """Validate Widget Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        if self.parametisation:
            if self.family.definitions.exclude(id=self.id).count() > 0:
                problems.append("Parametised widget %s:%s is not only widget defintion in family" % (self.url(),self.label))
        else:
            if self.family.definitions.filter(parametisation__isnull=False).count() > 0:
                problems.append("Non-parametised widget %s:%s has a paremetised widget defintion in the same family" % (self.url(),self.label))
        if not self.about:
            problems.append("Widget %s:%s has no 'about' information" % (self.url(), self.label))
        if self.viewwidgetdeclaration_set.all().count() == 0:
            problems.append("Widget %s:%s has no declarations" % (self.url(), self.label))
        default_tiles = self.tiles.filter(expansion=False).count()
        if default_tiles < 1:
            problems.append("Widget %s:%s has no default (non-expansion) tiles - must have at least one" % (self.url(), self.label))
        tiles = self.tiles.all()
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
        """
        Return the :model:`widget_data.WidgetData` object for this widget.

        view, pval: One of these must be supplied for a parametised widget.
        """
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
        """
        Returns the actual frequency display value.

        wd: If the :model:`widget_data.WidgetData` object is already available, it may be passed in directly.
        view, pval: One of these must be supplied for a parametised widget (unless a non-None wd has been passed in)
        """
        if not wd:
            wd = self.widget_data(view, pval)
        if wd and wd.actual_frequency_text:
            return wd.actual_frequency_text
        else:
            return self.default_frequency_text
    def __unicode__(self):
        return "%s (%s)" % (unicode(self.family), self.label)
    def data_last_updated(self, update=False, view=None, pval=None):
        """
        Return the date the data for this widget was last updated.

        update: If true, the objects last-updated cache is flushed and recalculated.
        view, pval: One of these must be supplied for a parametised widget (unless a non-None wd has been passed in)
        """
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
            for t in self.tiles.all():
                for ds in t.geo_datasets.all():
                    luds_mapdata.append(ds.data_last_updated(update))
            self._lud_cache = max_with_nulls(lud_statdata, lud_listdata, lud_graphdata, *luds_mapdata)
            return self._lud_cache
    class Meta:
        unique_together = (
            ("family", "label"),
        )
        ordering = ("family__subcategory", "sort_order")

