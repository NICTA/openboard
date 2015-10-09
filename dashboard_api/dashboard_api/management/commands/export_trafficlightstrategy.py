import json
from django.core.management.base import BaseCommand, CommandError

from dashboard_api.management.import_export import ImportExportException, export_trafficlightstrategy

class Command(BaseCommand):
    args="<strategy_url>"
    help = "Export named Traffic Light Strategy to stdout"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Must supply one and only one argument - the strategy url")
        try:
            data = export_trafficlightstrategy(args[0])
        except ImportExportException, e:
            raise CommandError(unicode(e))
        print >> self.stdout, json.dumps(data, indent=4)

