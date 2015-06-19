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
                        print >> self.stdout, "Correctly imported data for %s" % fam.url
                            
                    else:
                        raise CommandError("Incorrect import of %s  Re-export and compare to file %s" % (fam.url, jf))
                else:
                    print >> self.stdout, "Successfully imported data for %s" % fam.url
        except ImportExportException, e:
            raise CommandError(unicode(e))

