from django.contrib import admin

from rfs_loader.models import *

# Register your models here.

@admin.register(CurrentRating)
class CurrentRatingAdmin(admin.ModelAdmin):
    list_display = ("region", "last_featured")
