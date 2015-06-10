from django.db import models
from django.apps import apps

from widget_data.models import WidgetData, StatisticData, StatisticListItem, GraphData

from widget_def.models.reference import Location, Frequency

# Create your models here.

def max_with_nulls(*args):
    maxargs = []
    for arg in args:
        if arg is not None:
            maxargs.append(arg)
    if len(maxargs) == 0:
        return None
    elif len(maxargs) == 1:
        return maxargs[0]
    else:
        return max(*maxargs)

class WidgetDefinition(models.Model):
    _lud_cache = None
    family = models.ForeignKey("WidgetFamily")
    expansion_hint = models.CharField(max_length=80, blank=True, null=True)
    actual_location = models.ForeignKey(Location)
    actual_frequency = models.ForeignKey(Frequency)
    refresh_rate = models.IntegerField(help_text="in seconds")
    sort_order = models.IntegerField(unique=True)
    about = models.TextField(null=True, blank=True)
    def validate(self):
        """Validate Widget Definition. Return list of strings describing problems with the definition, i.e. an empty list indicates successful validation"""
        problems = []
        if not self.about:
            problems.append("Widget %s has no 'about' information" % self.url)
        if self.widgetdeclaration_set.all().count() == 0:
            problems.append("Widget %s has no declarations" % self.url)
        default_tiles = self.tiledefinition_set.filter(expansion=False).count()
        if default_tiles != 1:
            problems.append("Widget %s has %d default (non-expansion) tiles - must have one and only one" % (self.url, default_tiles))
        tiles = self.tiledefinition_set.all()
        if tiles.count() == default_tiles:
            if self.expansion_hint:
                problems.append("widget %s has no expansion tiles but expansion hint is set" % (self.url))
        else:
            if not self.expansion_hint:
                problems.append("widget %s has expansion tiles but expansion hint is not set" % (self.url))
        stat_urls = {}
        Statistic = apps.get_app_config("widget_def").get_model("Statistic")
        for stat in Statistic.objects.filter(tile__widget=self):
            if stat.url in stat_urls:
                problems.append("Widget %s has two statistics with url '%s' (in tiles %s and %s)" % (self.url, stat.url, stat.tile.url, stat_urls[stat.url]))
            else:
                stat_urls[stat.url] = stat.tile.url
        for tile in tiles:
            problems.extend(tile.validate())
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
    def widget_data(self):
        try:
            return WidgetData.objects.get(widget=self)
        except WidgetData.DoesNotExist:
            return None
    def actual_frequency_display(self):
        wd = self.widget_data()
        if wd and wd.actual_frequency_text:
            return wd.actual_frequency_text
        else:
            return self.actual_frequency.actual_display
    def __getstate__(self):
        return {
            "category": self.subcategory().category.name,
            "subcategory": self.subcategory().name,
            "name": self.name(),
            "subtitle": self.family.subtitle,
            "url": self.url(),
            "display": {
                "expansion_hint": self.expansion_hint,
                "tiles": [ tile.__getstate__() for tile in self.tiledefinition_set.all() ],
            },
            "source_url": self.source_url(),
            "source_url_text": self.family.source_url_text,
            "actual_frequency": self.actual_frequency_display(),
            "refresh_rate": self.refresh_rate,
            "about": self.about,
        }
    def export(self):
        return {
            "expansion_hint": self.expansion_hint,
            "actual_frequency_url": self.actual_frequency.url,
            "actual_location_url": self.actual_location.url,
            "refresh_rate": self.refresh_rate,
            "sort_order": self.sort_order,
            "about": self.about,
            "tiles": [ t.export() for t in self.tiledefinition_set.all() ],
            "declarations": [ wd.export() for wd in self.widgetdeclaration_set.all() ],
        }
    @classmethod
    def import_data(cls, family, data):
        try:
            w = WidgetDefinition.objects.get(family=family, actual_frequency__url=data["actual_frequency_url"], actual_location__url=data["actual_location_url"])
        except WidgetDefinition.DoesNotExist:
            w = WidgetDefinition(family=family,
                            actual_frequency=Frequency.objects.get(url=data["actual_frequency_url"]),
                            actual_location=Location.objects.get(url=data["actual_location_url"]))
        w.expansion_hint = data["expansion_hint"]
        w.refresh_rate = data["refresh_rate"]
        w.sort_order = data["sort_order"]
        w.about = data["about"]
        w.save()
        tile_urls = []
        TileDefinition = apps.get_app_config("widget_def").get_model("TileDefinition")
        for t in data["tiles"]:
            TileDefinition.import_data(w, t)
            tile_urls.append(t["url"])
        for tile in w.tiledefinition_set.all():
            if tile.url not in tile_urls:
                tile.delete()
        WidgetDeclaration = apps.get_app_config("widget_def").get_model("WidgetDeclaration")
        for d in data["declarations"]:
            wd=WidgetDeclaration.import_data(w, d)
        for wd in w.widgetdeclaration_set.all():
            found = False
            for decl in data["declarations"]:
                if wd.location.url == decl["location"] and wd.frequency.url == decl["frequency"]:
                    found = True
                    break
            if not found:
                wd.delete()
        return w
    def __unicode__(self):
        return "%s (%s, %s)" % (unicode(self.family), self.actual_location.name, self.actual_frequency.name)
    def data_last_updated(self, update=False):
        if self._lud_cache and not update:
            return self._lud_cache
        lud_statdata = StatisticData.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        lud_listdata = StatisticListItem.objects.filter(statistic__tile__widget=self).aggregate(lud=models.Max('last_updated'))['lud']
        lud_graphdata = GraphData.objects.filter(graph__tile__widget=self).aggregate(lud=models.Max("last_updated"))["lud"]
        self._lud_cache = max_with_nulls(lud_statdata, lud_listdata, lud_graphdata)
        return self._lud_cache
    class Meta:
        unique_together = (
            ("family", "actual_location", "actual_frequency"),
        )
        ordering = ("family__subcategory", "sort_order")

