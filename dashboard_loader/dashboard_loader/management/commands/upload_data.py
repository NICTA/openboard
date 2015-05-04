from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.models import Uploader

from dashboard_loader.loader_utils import LoaderException, do_upload, get_update_format

class Command(BaseCommand):
    args = "<app> [<filename> [<actual_frequency_display>]]"
    help = "Upload a file for the selected uploader. If no filename supplied, print the expected file format for the selected uploader. If supplied, the actual frequency display is updated (use quotes if new value contains white space)."
    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        if len(args) > 3:
            raise CommandError("Maxmimum of three arguments expected")
        elif len(args) == 0:
            raise CommandError("Must select an uploader app")

        appname = args[0]
        try:
            uploader = Uploader.objects.get(app=appname)
        except Uploader.DoesNotExist:
            raise CommandError("%s is not a registered uploader app" % appname)
        if len(args) == 1:
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
            fh = open(args[1], "r")
            if len(args) == 3:
                actual_freq_display = args[2]
            else:
                actual_freq_display = None
            messages = do_upload(uploader, fh, actual_freq_display, verbosity)
            for m in messages:
                print >> self.stdout, m

