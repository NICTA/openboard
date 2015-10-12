#   Copyright 2015 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
