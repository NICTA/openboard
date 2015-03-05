from django.contrib import admin
from django.contrib import messages
from widget_def.models import *

# Register your models here.

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order')

@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order')

class SubcategoryAdminInline(admin.TabularInline):
    model = Subcategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    inlines = [ SubcategoryAdminInline ]

class TrafficLightScaleCodeAdminInline(admin.TabularInline):
    model = TrafficLightScaleCode

@admin.register(TrafficLightScale)
class TrafficLightScaleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ TrafficLightScaleCodeAdminInline ]

class IconCodeAdminInline(admin.TabularInline):
    model = IconCode

@admin.register(IconLibrary)
class IconLibraryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ IconCodeAdminInline ]

class TileInline(admin.TabularInline):
    model = TileDefinition
    extra = 2

class DeclarationInline(admin.TabularInline):
    model = WidgetDeclaration
    extra = 2

@admin.register(WidgetDefinition)
class WidgetAdmin(admin.ModelAdmin):
    inlines = [DeclarationInline, TileInline]
    list_display = ('name', 'url', 'actual_frequency', 'subcategory', 'sort_order')
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

class StatisticInline(admin.StackedInline):
    model = Statistic
    extra = 2
    fieldsets = (
            (None, {
                'fields': ('name', 'name_as_label', 'url', 'stat_type', 'traffic_light_scale', 'icon_library', 'trend', 'hyperlinkable', 'sort_order'),
            }),
            ('Numeric', {
                'fields': ('num_precision', 'unit_prefix', 'unit_suffix', 'unit_underfix', 'unit_signed'),
                'description': "For numeric type statistics only",
                'classes': ('collapse',),
            }),
    )

@admin.register(TileDefinition)
class TileAdmin(admin.ModelAdmin):
    inlines = [StatisticInline]
    list_display = ('url', 'widget', 'expansion', 'sort_order')
    list_filter = ('widget',)

class GraphClusterInline(admin.StackedInline):
    model = GraphCluster
    extra = 2

class GraphDatasetInline(admin.StackedInline):
    model = GraphDataset
    extra = 2

@admin.register(GraphDefinition)
class GraphAdmin(admin.ModelAdmin):
    inlines = [ GraphClusterInline, GraphDatasetInline ]
    list_display = ('widget', 'tile')
    fieldsets = (
        (None, {
            'fields': ('tile', 'heading', 'graph_type'),
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
