import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_geowindow

class Command(BaseCommand):
    args="<name>"
    help = """Export named GeoWindow to stdout
    
(Put name in double quotes (") if it contains spaces)"""

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must supply one and only one argument - the GeoWindow name")
        try:
            data = export_geowindow(args[0])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

