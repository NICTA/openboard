from optparse import make_option
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    args = []
    help = "Run tests for all non-django installed apps."

    def handle(self, *args, **options):
        testable_apps = []
        for app in settings.INSTALLED_APPS:
            if not app.startswith("django."):
                testable_apps.append(app)
        call_command('test', *testable_apps, **options)
        return
