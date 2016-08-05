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

from dashboard_loader.models import Loader

from dashboard_loader.loader_utils import LoaderException
from dashboard_loader.management.update_data import update

class Command(BaseCommand):
    help = "Run selected loaders, or all loaders if none passed in"
    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", action="store_true", default=False, dest="force", help="Force loader to run")
        parser.add_argument("-V", "--VERBOSE", action="store_true", default=False, dest="super_verbose", help="Maximum verbosity")
        parser.add_argument('app', nargs="*", type=unicode)
    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        if options["super_verbose"]:
            verbosity = 10
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
        
