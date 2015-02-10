import datetime
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.models import Loader
from dashboard_loader.loader_utils import LoaderException

class Command(BaseCommand):
    args="[<app1> [<app2> ....]]"
    help = "Run selected loaders, or all loaders if none passed in"

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])

        if args:
            apps = []
            for arg in args:
                try:
                    app = Loader.objects.get(app=arg)
                    apps.append(app)
                except:
                    raise CommandError("%s is not a registered loader" % arg)
        else:
            apps = Loader.objects.all()

        for app in apps:
            if app.last_loaded:
                now = datetime.datetime.now()
                diff = now - last_loaded
                if diff.total_seconds() < app.refresh_rate:
                    continue
            _tmp = __import__(app.app + ".loader", globals(), locals(), ["update_data",], -1)
            update_data = _tmp.update_data
            try:
                update_data(app)
                if verbosity > 0:
                    print >> self.stdout, "Data updated for %s" % app.app
            except LoaderException, e:
                raise CommandError(u"Update of %s failed: %s" % (app.app, unicode(e)))
        return
        
