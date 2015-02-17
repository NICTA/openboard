import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_widget

class Command(BaseCommand):
    args="<url> <actual_frequency_url"
    help = "Export named Widget Defintion to stdout"

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("Must supply two and only two arguments - the widget url and the actual frequency url")
        try:
            data = export_widget(args[0], args[1])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

