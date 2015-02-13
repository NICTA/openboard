from django.contrib import admin
from django.contrib import messages
from dashboard_loader.models import Loader
from dashboard_loader.management.update_data import update
from dashboard_loader.loader_utils import LoaderException

@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):
    list_display=("app", "refresh_rate", "suspended", "last_loaded")
    list_editable=("refresh_rate", "suspended")
    fields = ('refresh_rate', 'suspended')
    list_filter=("suspended",)
    readonly_fields=("app", "last_loaded")
    actions = [ 'update_data' ]
    def update_data(self, request, queryset):
        infos = []
        errors = []
        for l in queryset:
            try:
                infos.extend(update(l, verbosity=3, force=True))
            except LoaderException, e:
                errors.append(unicode(e))
        for err in errors:
            self.message_user(request, err, level=messages.ERROR)
        for msg in infos:
            self.message_user(request, msg)
    update_data.short_description = "Update data for Loader"


