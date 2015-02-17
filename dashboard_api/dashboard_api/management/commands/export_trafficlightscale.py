import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_trafficlightscale

class Command(BaseCommand):
    args="<library_name>"
    help = "Export named Traffic Light Scale to stdout"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must supply one and only one argument - the scale name")
        try:
            data = export_trafficlightscale(args[0])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

