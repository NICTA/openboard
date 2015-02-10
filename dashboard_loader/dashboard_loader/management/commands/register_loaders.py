from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.management.register_loaders import register_loaders

class Command(BaseCommand):
    args = ""
    help = "Update registration of all loaders"

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        register_loaders(verbosity, self.stdout) 
        
