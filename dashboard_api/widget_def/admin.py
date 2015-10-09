from django.contrib.gis import admin
from django.contrib import messages
from widget_def.models import *

# Register your models here.

# @admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'requires_authentication', 'sort_order')

admin.site.register(Theme, ThemeAdmin)

# @admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order')

admin.site.register(Location, LocationAdmin)

# @admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'actual_display', 'url', 'display_mode', 'sort_order')

admin.site.register(Frequency, FrequencyAdmin)

class SubcategoryAdminInline(admin.TabularInline):
    model = Subcategory

# @admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    inlines = [ SubcategoryAdminInline ]

admin.site.register(Category, CategoryAdmin)
    
class TrafficLightScaleCodeAdminInline(admin.TabularInline):
    model = TrafficLightScaleCode

# @admin.register(TrafficLightScale)
class TrafficLightScaleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ TrafficLightScaleCodeAdminInline ]

admin.site.register(TrafficLightScale, TrafficLightScaleAdmin)

class TrafficLightAutoRuleAdminInline(admin.TabularInline):
    model = TrafficLightAutoRule
    extra = 2
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if len(request.resolver_match.args) == 1:
            strategy = TrafficLightAutoStrategy.objects.get(id=int(request.resolver_match.args[0]))
            if db_field.name == "code":
                kwargs["queryset"] = strategy.scale.trafficlightscalecode_set.all()
        return super(TrafficLightAutoRuleAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class TrafficLightAutoStrategyAdmin(admin.ModelAdmin):
    list_display = ("url", "scale")
    inlines = [ TrafficLightAutoRuleAdminInline ]
    actions = ['validate']
    def validate(self, request, queryset):
        problems = []
        for s in queryset:
            problems.extend(s.validate())
        if not problems:
            self.message_user(request, "Traffic Light Strategies validated OK")
        for problem in problems:
            self.message_user(request, problem, level=messages.ERROR)
    validate.short_description = "Check Traffic Light Auto Strategies for errors"

admin.site.register(TrafficLightAutoStrategy, TrafficLightAutoStrategyAdmin)

class TrafficLightAutomationAdmin(admin.ModelAdmin):
    list_display = ("url", "strategy")
    actions = ["validate"]
    def validate(self, request, queryset):
        problems = []
        for s in queryset:
            problems.extend(s.validate())
        if not problems:
            self.message_user(request, "Traffic Light Automations validated OK")
        for problem in problems:
            self.message_user(request, problem, level=messages.ERROR)
    validate.short_description = "Check Traffic Light Automations for errors"

admin.site.register(TrafficLightAutomation, TrafficLightAutomationAdmin)

class IconCodeAdminInline(admin.TabularInline):
    model = IconCode

# @admin.register(IconLibrary)
class IconLibraryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ IconCodeAdminInline ]

admin.site.register(IconLibrary, IconLibraryAdmin)

# @admin.register(WidgetFamily)
class WidgetFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'subtitle', 'url', 'subcategory')

admin.site.register(WidgetFamily, WidgetFamilyAdmin)

class TileInline(admin.TabularInline):
    exclude = ( "template", "geo_window", "geo_datasets")
    model = TileDefinition
    extra = 2

class DeclarationInline(admin.TabularInline):
    model = WidgetDeclaration
    extra = 2

# @admin.register(WidgetDefinition)
class WidgetAdmin(admin.ModelAdmin):
    inlines = [DeclarationInline, TileInline]
    list_display = ('family', 'subtitle', 'actual_location', 'actual_frequency', 'subcategory', 'sort_order')
    actions = ['validate']
    readonly_fields=('data_last_updated',)
    def validate(self, request, queryset):
        problems = []
        for w in queryset:
            problems.extend(w.validate())
        if not problems:
            self.message_user(request, "Widget Definitions validated OK")
        for problem in problems:
            self.message_user(request, problem, level=messages.ERROR)
    validate.short_description = "Check Widget Definitions for errors"

admin.site.register(WidgetDefinition, WidgetAdmin)

class StatisticInline(admin.StackedInline):
    model = Statistic
    extra = 2
    fieldsets = (
            (None, {
                'fields': ('name', 'name_as_label', 'url', 'stat_type', 'traffic_light_scale', 'traffic_light_automation', 'icon_library', 'trend', 'rotates', 'hyperlinkable', 'numbered_list', 'footer', 'editable', 'sort_order'),
            }),
            ('Numeric', {
                'fields': ('num_precision', 'unit_prefix', 'unit_si_prefix_rounding', 'unit_suffix', 'unit_underfix', 'unit_signed'),
                'description': "For numeric type statistics only",
                'classes': ('collapse',),
            }),
    )

# @admin.register(TileDefinition)
class TileAdmin(admin.ModelAdmin):
    inlines = [StatisticInline]
    list_display = ('url', 'widget', 'expansion', 'sort_order')
    list_filter = ('widget',)

admin.site.register(TileDefinition, TileAdmin)

class PointColourRangeInline(admin.StackedInline):
    model = PointColourRange
    extra = 2

# @admin.register(PointColourMap)
class PointColourMapAdmin(admin.ModelAdmin):
    inlines = [PointColourRangeInline]
    list_display = ('label',)

admin.site.register(PointColourMap, PointColourMapAdmin)

class GraphClusterInline(admin.StackedInline):
    model = GraphCluster
    extra = 2

class GraphDatasetInline(admin.StackedInline):
    model = GraphDataset
    extra = 2

class GraphOptionInline(admin.StackedInline):
    model = GraphDisplayOptions
    extra = 2

# @admin.register(GraphDefinition)
class GraphAdmin(admin.ModelAdmin):
    inlines = [ GraphOptionInline, GraphClusterInline, GraphDatasetInline ]
    list_display = ('widget', 'tile')
    fieldsets = (
        (None, {
            'fields': ('tile', 'heading', 'graph_type',),
         }),
        ('Numeric Axes', {
            'fields': ('numeric_axis_label', 'numeric_axis_always_show_zero',
                    'use_secondary_numeric_axis',
                    'secondary_numeric_axis_label', 'secondary_numeric_axis_always_show_zero',),
            'description': 'Not used for Pie Charts',
            'classes': ('collapse',),
         }),
        ('Horizontal Axis', {
            'fields': ('horiz_axis_label', 'horiz_axis_type'),
            'description': 'Only used for Line Graphs',
            'classes': ('collapse',),
         }),
    )

admin.site.register(GraphDefinition, GraphAdmin)

class RawDataSetColumnInline(admin.StackedInline):
    model = RawDataSetColumn
    extra = 2

# @admin.register(RawDataSet)
class RawDataSetAdmin(admin.ModelAdmin):
    inlines = [ RawDataSetColumnInline ]
    list_display = ("widget", "url")

admin.site.register(RawDataSet, RawDataSetAdmin)

class GridColumnInline(admin.StackedInline):
    model = GridColumn
    extra = 2

class GridRowInline(admin.StackedInline):
    model = GridRow
    extra = 2

class GridStatisticInline(admin.StackedInline):
    model = GridStatistic
    extra = 2
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if len(request.resolver_match.args) == 1:
            grid = GridDefinition.objects.get(id=int(request.resolver_match.args[0]))
            if db_field.name == "column":
                kwargs["queryset"] = GridColumn.objects.filter(grid=grid)
            elif db_field.name == "row":
                kwargs["queryset"] = GridRow.objects.filter(grid=grid)
            elif db_field.name == "statistic":
                kwargs["queryset"] = Statistic.objects.filter(tile=grid.tile)
        return super(GridStatisticInline, self).formfield_for_foreignkey(db_field,
                        request, **kwargs)

# @admin.register(GridDefinition)
class GridAdmin(admin.ModelAdmin):
    inlines = [ GridColumnInline, GridRowInline, GridStatisticInline ]
    list_display = ("widget", "tile")

admin.site.register(GridDefinition, GridAdmin)

# @admin.register(GeoWindow)
class GeoWindowAdmin(admin.GeoModelAdmin):
    default_lon=134.435
    default_lat=-26.237

admin.site.register(GeoWindow, GeoWindowAdmin)

class GeoColourPointInline(admin.StackedInline):
    model = GeoColourPoint
    extra = 2

# @admin.register(GeoColourScale)
class GeoColourScaleAdmin(admin.ModelAdmin):
    inlines = [GeoColourPointInline,]
    list_display = ('url',)

admin.site.register(GeoColourScale, GeoColourScaleAdmin)

class GeoPropertyInline(admin.StackedInline):
    model=GeoPropertyDefinition
    extra=2

class GeoDatasetDeclarationInline(admin.StackedInline):
    model=GeoDatasetDeclaration
    extra=2

# @admin.register(GeoDataset)
class GeoDatasetAdmin(admin.ModelAdmin):
    inlines = [GeoPropertyInline, GeoDatasetDeclarationInline]
    list_display = ['url', 'label', 'geom_type']
    actions = ["validate"]
    def validate(self, request, queryset):
        problems = []
        for ds in queryset:
            problems.extend(ds.validate())
        if not problems:
            self.message_user(request, "Widget Definitions validated OK")
        for problem in problems:
            self.message_user(request, problem, level=messages.ERROR)
    validate.short_description = "Check Geo-Dataset for errors"

admin.site.register(GeoDataset, GeoDatasetAdmin)

