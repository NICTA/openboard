import datetime
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.models import Loader
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import LoaderException, update_loader, lock_update

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
        tz = pytz.timezone(settings.TIME_ZONE)
        for app in apps:
            if app.last_loaded:
                now = datetime.datetime.now(tz)
                diff = now - app.last_loaded
                if diff.total_seconds() < app.refresh_rate:
                    if verbosity >= 3:
                        print >> self.stdout, "Loader %s not due for refresh until %s" % (app.app, (app.last_loaded + datetime.timedelta(seconds=app.refresh_rate)).astimezone(tz).strftime("%d/%m/%Y %H:%M:%S"))
                    continue
            _tmp = __import__(app.app + ".loader", globals(), locals(), ["update_data",], -1)
            update_data = _tmp.update_data
            try:
                if lock_update(app):
                    update_data(app, verbosity=verbosity, logger=self.stdout)
                    update_loader(app)
                    if verbosity > 0:
                        print >> self.stdout, "Data updated for %s" % app.app
                elif verbosity > 0:
                    print >> self.stdout, "Data update for %s is locked by another update process" % app.app
            except LoaderException, e:
                raise CommandError(u"Update of %s failed: %s" % (app.app, unicode(e)))
        return
        
