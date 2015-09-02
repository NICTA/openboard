from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.loader_utils import LoaderException, geo_upload

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("uploader", type=unicode)
        parser.add_argument("url", type=unicode)
        parser.add_argument("filename", nargs="?", type=unicode, default=None)
        
    def handle(self, uploader, url, filename, **options):
        verbosity = int(options["verbosity"])
        try:
            messages = geo_upload(uploader, filename, url, verbosity)
            for m in messages:
                print >> self.stdout, m
        except LoaderException, e:
            raise CommandError(unicode(e))

