#   Copyright 2015, 2016 NICTA
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

import json
import sys

from django.core.management.base import BaseCommand, CommandError
from widget_def.models import GeoDataset, GeoPropertyDefinition, ViewGeoDatasetDeclaration

class Command(BaseCommand):
    help = "Convert a raw data set export to a geo data set"
    def add_arguments(self, parser):
        parser.add_argument("-c", "--category",
            action="store", type="string", 
            default=None, dest="category",
            help="Use this category for the geo dataset instead of that used in the raw dataset")
        parser.add_argument("-s", "--subcategory",
            action="store", type="string", 
            default=None, dest="subcategory",
            help="Use this subcategory for the geo dataset instead of that used in the raw dataset")
        parser.add_argument("-u", "--url",
            action="store", type="string", 
            default=None, dest="url",
            help="Use this url for the geo dataset instead of that used in the raw dataset")
        parser.add_argument("-o", "--order",
            action="store", type="int", 
            default=100, dest="order",
            help="Use this sort_order for the geo dataset - defaults to 100")
        parser.add_argument("-l", "--label",
            action="store", type="string", 
            default=None, dest="label",
            help="Use this label for the geo dataset - otherwise use the widget family name")
        parser.add_argument("widget.json", type=unicode)
        parser.add_argument("rds_url", type=unicode)
    def handle(self, *args, **options):
        widget_file = options["widget.json"]
        rds_url = options["rds_url"]
        verbosity = options["verbosity"]
        category = options["category"]
        subcategory = options["subcategory"]
        order = options["order"]
        label = options["label"]
        geo_url = options["url"]
        if not geo_url:
            geo_url = rds_url
        try:
            wf = open(widget_file, "r")
        except Exception, e:
            raise CommandError("Cannot open widget file: %s" % unicode(e)) 
        try:
            w = json.load(wf)
        except Exception, e:
            raise CommandError("Cannot parse json in widget file: %s" % unicode(e))
        wf.close()
        if verbosity > 0:
            print >> self.stderr, "Widget file read"
        rds = None
        for wd in w["definitions"]:
            for raw in wd["raw_data_sets"]:
                if raw["url"] == rds_url:
                    rds = raw
                    break
        if not rds:
            raise CommandError("Cannot find url %s in widget file" % rds_url)
        if verbosity > 1:
            print >> self.stderr, "RDS %s found" % rds_url
        output = {}
        if category:
            output["category"] = category
        else:
            output["category"] = w["category"]
        if subcategory:
            output["subcategory"] = subcategory
        else:
            output["subcategory"] = w["subcategory"]
        output["url"] = geo_url
        output["sort_order"] = order
        output["geom_type"] = GeoDataset.PREDEFINED
        if label:
            output["label"] = label
        else:
            output["label"] = w["name"]
        output["view_declarations"] = []
        output["properties"] = []
        first_column = True
        for column in rds["columns"]:
            prop = {
                "url": column["url"],
                "sort_order": column["sort_order"],
                "label": column["heading"],
                "predefined_geom_property": first_column,
                "data_property": not first_column,
            }
            if first_column:
                prop["type"] = GeoPropertyDefinition.STRING
                prop["num_precision"] = None
            else:
                prop["type"] = GeoPropertyDefinition.NUMERIC
                prop["num_precision"] = 0
            output["properties"].append(prop)
            first_column = False
        json.dump(output, sys.stdout, indent=4)
        if verbosity > 1:
            print >> self.stderr, "Done"
