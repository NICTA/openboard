import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_geocolourscale

class Command(BaseCommand):
    args="<url>"
    help = """Export indicated GeoColourScale to stdout"""

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must supply one and only one argument - the GeoColourScale url")
        try:
            data = export_geocolourscale(args[0])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

