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
from django.core.management.base import BaseCommand, CommandError

from dashboard_loader.loader_utils import LoaderException, geo_upload
from dashboard_loader.geoloader import load_geodata

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dummy_data",
                    action="store", type=unicode, metavar="FIELD_NAME",
                    default=None, dest="dummy_data",
                    help="Add a dummy data property with random values in the range 0 to 100.")
        parser.add_argument("-s", "--simplify",
                    action="store", type=float, metavar="TOLERANCE",
                    default=None, dest="simplify",
                    help="Simplify geometries to the specified tolerance.")
        parser.add_argument("-i", "--srid",
                    action="store", type=int, metavar="SRID",
                    default=None, dest="srid",
                    help="Convert all coordinates from the specified SRID to SRID 4283 (GDA94).")
        parser.add_argument("-l", "--layer",
                    action="store", type=int, metavar="LAYER_NUM",
                    default=0, dest="layer_num",
                    help="Load data from the numbered layer.  (Note that the first layer is numbered zero - the default.)")
        parser.add_argument("-P", "--capitalise_properties",
                    action="store_true", default=False,
                    dest="capitalise_properties",
                    help="Convert all property names to upper case (e.g. for shp files)")
        parser.add_argument("url", type=unicode)
        parser.add_argument("filename", nargs="?", type=unicode, default=None)
        
    def handle(self, url, filename, **options):
        try:
            messages = load_geodata(filename, url, **options)
            for m in messages:
                print >> self.stdout, m
        except LoaderException, e:
            raise CommandError(unicode(e))

