import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_widget

class Command(BaseCommand):
    args="<url> <actual_location_url> <actual_frequency_url>"
    help = "Export named Widget Defintion to stdout"

    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError("Must supply three and only three arguments - the widget url, the actual location url and the actual frequency url")
        try:
            data = export_widget(args[0], args[1], args[2])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

