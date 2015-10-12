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

import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_widget_data
from dashboard_loader.management.import_widget_data import import_widget_data

class Command(BaseCommand):
    args="<json_file> ..."
    help = "Import named widget data json export files"
    # option_list = BaseCommand.option_list + (
    #           make_option("-t", "--test",
    #                   action="store_true", default=False, dest="test",
    #                   help="Test that data imported correctly"),
    #       )
    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Must supply at least one json file to import")
        verbosity = options["verbosity"]
    #   test = options["test"]
        test = False
        try:
            for jf in args:
                f = open(jf)
                data = json.load(f)
                fam = import_widget_data(data)
                f.close()
                if test:
                    # Will always fail because of last_updated date
                    data1 = export_widget_data(fam)
                    if export_widget_data(fam) == data:
                        if verbosity > 0:
                            print >> self.stdout, "Correctly imported data for %s" % fam.url
                            
                    else:
                        raise CommandError("Incorrect import of %s  Re-export and compare to file %s" % (fam.url, jf))
                else:
                    if verbosity > 0:
                        print >> self.stdout, "Successfully imported data for %s" % fam.url
        except ImportExportException, e:
            raise CommandError(unicode(e))

