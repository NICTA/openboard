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

import datetime
import pytz

from django.conf import settings

from dashboard_loader.models import Loader
from dashboard_loader.loader_utils import do_update
from dashboard_loader.tasks import update_app_data

def update(loader, verbosity=0, force=False, async=True):
    if not isinstance(loader, Loader):
        try:
            loader = Loader.objects.get(app=loader)
        except Loader.DoesNotExist:
            return [u"%s not a valid loader" % unicode(loader) ]
    if not force:
        reason = loader.reason_to_not_run()
        if reason:
            if verbosity >= 3:
                return [ reason ]
            else:
                return []
    if async:
        update_app_data.delay(loader.app)
        return ["Update of app %s started" % loader.app]
    else:
        return do_update(loader.app, verbosity=verbosity, force=True)

