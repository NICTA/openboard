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

