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

from django.core.management.base import BaseCommand, CommandError

from dashboard_loader_app.models import Uploader

from dashboard_loader.loader_utils import LoaderException, do_upload, get_update_format

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("uploader", type=unicode)
        parser.add_argument("filename", nargs="?", type=unicode, default=None)
        parser.add_argument("actual_frequency_display", nargs="?", type=unicode, default=None)
        
    help = "Upload a file for the selected uploader. If no filename supplied, print the expected file format for the selected uploader. If supplied, the actual frequency display is updated (use quotes if new value contains white space)."
    def handle(self, uploader, filename, actual_frequency_display, **options):
        verbosity = int(options["verbosity"])

        appname = uploader
        try:
            uploader = Uploader.objects.get(app=appname)
        except Uploader.DoesNotExist:
            raise CommandError("%s is not a registered uploader app" % appname)
        if not filename:
            # print format
            fmt = get_update_format(appname)
            output = []
            output.append("File format for %s uploads" % appname)
            output.append("=====================================")
            output.append("")
            output.append("Format: %s" % fmt["format"])
            if len(fmt["sheets"]) > 1:
                output.append("Work Sheets:")
                output.append("============")
            for sheet in fmt["sheets"]:
                if len(fmt["sheets"]) > 1:
                    output.append(sheet["name"])
                    output.append("--------------")
                output.append("Columns:")
                for col in sheet["cols"]:
                    output.append("\t%s: %s" % (col[0], col[1]))
                output.append("Rows:")
                for row in sheet["rows"]:
                    output.append("\t%s: %s" % (row[0], row[1]))
                if sheet.get("notes"):
                    output.append("Notes:")
                    for note in sheet["notes"]:
                        output.append("\t* %s" % note)
            print >> self.stdout, "\n".join(output)
        else:
            fh = open(filename, "r")
            messages = do_upload(uploader, fh, actual_frequency_display, verbosity)
            for m in messages:
                print >> self.stdout, m

