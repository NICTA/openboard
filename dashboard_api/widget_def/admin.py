from django.contrib import admin
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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')

class TrafficLightScaleCodeAdminInline(admin.TabularInline):
    model = TrafficLightScaleCode

@admin.register(TrafficLightScale)
class TrafficLightScaleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ TrafficLightScaleCodeAdminInline ]

class TileInline(admin.TabularInline):
    model = TileDefinition
    extra = 2

class DeclarationInline(admin.TabularInline):
    model = WidgetDeclaration
    extra = 2

@admin.register(WidgetDefinition)
class WidgetAdmin(admin.ModelAdmin):
    inlines = [DeclarationInline, TileInline]
    list_display = ('name', 'url', 'actual_frequency', 'category', 'sort_order')

class StatisticInline(admin.StackedInline):
    model = Statistic
    extra = 2
    fieldsets = (
            (None, {
                'fields': ('name', 'stat_type', 'traffic_light_scale', 'trend', 'sort_order'),
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
    filter_verticali = ('widget',)
    


