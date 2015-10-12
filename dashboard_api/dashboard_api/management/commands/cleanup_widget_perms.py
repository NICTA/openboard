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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from widget_def.models import WidgetFamily

class Command(BaseCommand):
    args=""
    help = "Cleanup Widget Family permissions"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("No arguments expected")
        perms = []
        all_perms = []
        for wf in WidgetFamily.objects.all():
            p = wf.edit_permission(log=self.stdout)
            perms.append(p.codename)
            p = wf.edit_all_permission(log=self.stdout)
            all_perms.append(p.codename)
        ct = ContentType.objects.get_for_model(WidgetFamily)
        for p in Permission.objects.filter(content_type=ct,
                        codename__startswith="w_"):
            if p.codename not in perms:
                print >> self.stdout, "Deleted unused permission: %s" % p.codename
                p.delete()
        for p in Permission.objects.filter(content_type=ct,
                        codename__startswith="wa_"):
            if p.codename not in all_perms:
                print >> self.stdout, "Deleted unused permission: %s" % p.codename
                p.delete()

