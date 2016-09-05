#   Copyright 2015 NICTA
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

from django.contrib import admin
from django.contrib import messages
from dashboard_loader.models import Loader
from dashboard_loader.management.update_data import update
from dashboard_loader.loader_utils import LoaderException

@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):
    list_display=("app", "refresh_rate", "suspended", "last_locked", "last_run", "last_loaded")
    list_editable=("refresh_rate", "suspended")
    fields = ('app', 'refresh_rate', 'suspended', 'last_loaded', 'last_run', "last_locked", "locked_by_process", "locked_by_thread", "last_api_access")
    list_filter=("suspended",)
    readonly_fields=("app", "last_loaded", "last_run", "locked_by_process", "locked_by_thread")
    actions = [ 'update_data' ]
    def update_data(self, request, queryset):
        infos = []
        errors = []
        for l in queryset:
            try:
                infos.extend(update(l, verbosity=3, force=True, async=False))
            except LoaderException, e:
                errors.append(unicode(e))
        for err in errors:
            self.message_user(request, err, level=messages.ERROR)
        for msg in infos:
            self.message_user(request, msg)
    update_data.short_description = "Update data for Loader"


