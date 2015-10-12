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

from dashboard_loader.management.register_loaders import register_loaders

class Command(BaseCommand):
    args = ""
    help = "Update registration of all loaders"

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        register_loaders(verbosity, self.stdout) 
        
