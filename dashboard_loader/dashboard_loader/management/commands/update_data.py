from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.models import Loader

from dashboard_loader.loader_utils import LoaderException
from dashboard_loader.management.update_data import update

class Command(BaseCommand):
    args="[<app1> [<app2> ....]]"
    help = "Run selected loaders, or all loaders if none passed in"
    option_list = BaseCommand.option_list + (
                make_option("-f", "--force",
                        action="store_true", default=False, dest="force",
                        help="Force loader to run"),
            )

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
            try:
                messages = update(app, verbosity=verbosity, 
                                force=options["force"], async=False)
                for msg in messages:
                    print >> self.stdout, msg
            except LoaderException, e:
                raise CommandError(u"Update of %s failed: %s" % (app.app, unicode(e)))
        return
        
