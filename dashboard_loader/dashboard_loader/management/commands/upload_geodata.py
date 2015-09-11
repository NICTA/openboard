from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.loader_utils import LoaderException, geo_upload

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dummy_data",
                    action="store", type=unicode, metavar="FIELD_NAME",
                    default=None, dest="dummy_data",
                    help="Add a dummy data property with random values in the range 0 to 100. Not supported by all uploaders.")
        parser.add_argument("-s", "--simplify",
                    action="store", type=float, metavar="TOLERANCE",
                    default=None, dest="simplify",
                    help="Simplify geometries to the specified tolerance. Not supported by all uploaders.")
        parser.add_argument("uploader", type=unicode)
        parser.add_argument("url", type=unicode)
        parser.add_argument("filename", nargs="?", type=unicode, default=None)
        
    def handle(self, uploader, url, filename, **options):
        try:
            messages = geo_upload(uploader, filename, url, **options)
            for m in messages:
                print >> self.stdout, m
        except LoaderException, e:
            raise CommandError(unicode(e))

