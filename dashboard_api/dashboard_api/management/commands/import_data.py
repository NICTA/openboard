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

from dashboard_api.management.import_export import ImportExportException, import_data

class Command(BaseCommand):
    args="<json_file> ..."
    help = "Import named json export files"
    option_list = BaseCommand.option_list + (
                make_option("-t", "--test",
                        action="store_true", default=False, dest="test",
                        help="Test that data imported correctly"),
                make_option("-m", "--merge",
                        action="store_true", default=False, dest="merge",
                        help="Do not delete objects not included in file (for categories and views import files only)"),
            )
    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Must supply at least one json file to import")
        test = options["test"]
        verbosity = options["verbosity"]
        try:
            for jf in args:
                print "Loading ", jf
                f = open(jf)
                data = json.load(f)
                obj = import_data(data, merge=options["merge"])
                f.close()
                if test:
                    if obj.export() == data:
                        if verbosity > 0:
                            print >> self.stdout, "Correctly imported %s: %s" % (
                                obj.__class__.__name__,
                                unicode(obj)
                                )
                    else:
                        raise CommandError("Incorrect import of %s: %s  Re-export and compare to file %s" % (
                            jf,
                            obj.__class__.__name__,
                            unicode(obj)
                            ))
                else:
                    if verbosity > 0:
                        print >> self.stdout, "Successfully imported %s: %s" % (
                                obj.__class__.__name__,
                                unicode(obj)
                                )
        except ImportExportException, e:
            raise CommandError(unicode(e))

