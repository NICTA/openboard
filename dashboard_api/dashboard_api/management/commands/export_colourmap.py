import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_pointcolourmap

class Command(BaseCommand):
    args="<url>"
    help = "Export named Point Colour Map to stdout"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must supply one and only one argument - the Point Colour Map label")
        try:
            data = export_pointcolourmap(args[0])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

