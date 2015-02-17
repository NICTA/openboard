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
            )
    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Must supply at least one json file to import")
        test = options["test"]
        try:
            for jf in args:
                f = open(jf)
                data = json.load(f)
                obj = import_data(data)
                f.close()
                if test:
                    if obj.export() == data:
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
                    print >> self.stdout, "Successfully imported %s: %s" % (
                            obj.__class__.__name__,
                            unicode(obj)
                            )
        except ImportExportException, e:
            raise CommandError(unicode(e))

