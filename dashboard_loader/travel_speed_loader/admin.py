from django.contrib import admin
from travel_speed_loader.models import *
# Register your models here.

@admin.register(RoadSection)
class RoadSectionAdmin(admin.ModelAdmin):
    list_display = ("road", "route_direction", "label", "origin", "destination", "length")
    list_editable = ("length",)
    list_filter = ("road", "route_direction")
    fields = ("length",)
    read_only_fields = ("road", "label", "origin", "destination", "direction")

@admin.register(Road)
class RoadSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "am_direction", "pm_direction")
    list_editable = ("am_direction", "pm_direction",)

