#   Copyright 2016 CSIRO
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

from django.core.management.base import BaseCommand, CommandError
from django.core import management
import os

from dashboard_loader.models import Uploader

from dashboard_loader.loader_utils import LoaderException, do_upload

class Command(BaseCommand):
    help = "Run all coag dashboard uploaders, using the xlsx files in the uploader directories."
    def handle(self, **options):
        verbosity = int(options["verbosity"])

        for uploader in Uploader.objects.all():
            appname = uploader.app
            if appname == "coag_uploader":
                continue
            filename_base = appname.rsplit('_', 1)[0]
            management.call_command('upload_data', appname, os.path.join(appname, filename_base + ".xlsx"), "unused", verbosity=verbosity)

