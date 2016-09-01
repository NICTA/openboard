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

import sys
import traceback
from importlib import import_module

from dashboard_loader.registry import register
from dashboard_loader.models import Loader, Uploader
from django.apps import apps

def register_loaders(verbosity, logger):
    registered_app_loaders = []
    registered_app_uploaders = []
    for app in apps.get_app_configs():
        if app.name.startswith('django'):
            continue
        if app.name in ('widget_def', 'widget_data', 'dashboard_loader', 'dashboard_api'):
            continue
        if verbosity >= 3:
            print >> logger, "Checking app %s" % app.name
        try:
            refresh_rate = import_module(app.name + ".loader").refresh_rate
            old_rate = register(app.name, refresh_rate)
            registered_app_loaders.append(app.name)
            if old_rate is None:
                if verbosity > 0:
                    print >> logger, "App %s loader registered (suspended)" % app.name
            elif old_rate == refresh_rate:
                if verbosity >= 2:
                    print >> logger, "App %s loader already registered" % app.name
            else:
                if verbosity > 0:
                    print >> logger, "Refresh rate for app %s loader updated from %s to %s" % (app.name, old_rate, refresh_rate)
        except (ImportError, AttributeError), e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if verbosity >= 2:
                print >> logger, "App %s is not a Loader" % app.name
            if verbosity >= 3:
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                              file=sys.stdout)
        try:
            candidate_uploader = import_module(app.name + ".uploader")
            upload_file = candidate_uploader.upload_file
            file_format = candidate_uploader.file_format
            new = register(app.name)
            registered_app_uploaders.append(app.name)
            if new:
                if verbosity > 0:
                    print >> logger, "App %s uploader registered" % app.name
            else:
                if verbosity >= 3:
                    print >> logger, "App %s uploader already registered" % app.name
        except (ImportError, AttributeError):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if verbosity >= 2:
                print >> logger, "App %s is not an uploader" % app.name
            if verbosity >= 3:
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                              file=sys.stdout)
    for l in Loader.objects.all():
        if l.app not in registered_app_loaders:
            l.delete()
            if verbosity > 0:
                print >> logger, "App %s loader deregistered" % l.app
    for u in Uploader.objects.all():
        if u.app not in registered_app_uploaders:
            u.permission().delete()
            u.delete()
            if verbosity > 0:
                print >> logger, "App %s uploader deregistered" % u.app
    return
