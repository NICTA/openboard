import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_categories

class Command(BaseCommand):
    help = "Export all categories and subcategories"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("No arguments are required")
        try:
            data = export_categories()
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

