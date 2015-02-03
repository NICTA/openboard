from django.contrib import admin
from widget_def.models import *

# Register your models here.

admin.site.register(Theme)
admin.site.register(Location)
admin.site.register(Frequency)

admin.site.register(Category)

admin.site.register(WidgetDefinition)
admin.site.register(TileDefinition)

admin.site.register(TrafficLightScale)
admin.site.register(TrafficLightScaleCode)
admin.site.register(Statistic)

