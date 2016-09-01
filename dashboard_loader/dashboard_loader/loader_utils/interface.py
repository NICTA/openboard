#   Copyright 2015 CSIRO
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
import os
import thread

from django.conf import settings
from django.db import transaction
from importlib import import_module

from dashboard_loader.models import Loader, Uploader

# Default Timezone for datetimes, as configured in settings
tz = pytz.timezone(settings.TIME_ZONE)

class LoaderException(Exception):
    "Exception thrown by Loader API"
    pass

@transaction.atomic
def lock_update(app):
    try:
        loader = Loader.objects.get(app=app)
    except Loader.DoesNotExist:
        return None
    if loader.locked_by_process:
        try:
            os.getpgid(loader.locked_by_process)
            return loader
        except OSError:
            pass
    loader.lock()
    loader.save()
    return loader

def unlock_loader(loader):
    loader.locked_by_process = None
    loader.locked_by_thread = None
    loader.save()

def update_loader(loader, success=True):
    loader.last_run = datetime.datetime.now(tz)
    if success:
        loader.last_loaded = loader.last_run
    unlock_loader(loader)

def do_update(app, verbosity=0, force=False):
    """Run a loader module, unless it is already locked by another thread.

app: The name of the loader module to be run.
verbosity: The verbosity level, 0-3.  Higher numbers = more verbosity.
           (default=0)
force: If False, only run the loader if it has not been run within it's
       refresh window and it is not suspended.  If True, ignore these
       checks and run anyway.
       (default=False)

Returns a list of messages (strings).

A loader module is a python package containing a python module loader.py 
that defines:

    1) An integer variable "refresh_rate" containing the default time
       to wait between loads for the loader module (in seconds).
    2) A function update_data that performs the actual load, returns a 
       list of messages (strings) and takes two arguments:
       a) loader:  The dashboard_loader.models.Loader registration object 
          for the loader module.
       b) verbosity: The verbosity level, 0-3.  
          Higher numbers = more verbosity. (default=0)

Loader modules must be registered with dashboard_loader application. To
register a loader module, add it to the "INCLUDED_APPS" setting and
run the "register_loaders" django command.
"""
    update_data = import_module(app + ".loader").update_data
    loader = lock_update(app)
    if loader.locked_by_me():
        reason = loader.reason_to_not_run()
        if not reason or force:
            try:
                messages = update_data(loader, verbosity=verbosity)
            except LoaderException, e:
                update_loader(loader, False)
                return [ "Data update for %s failed: %s" % (app, unicode(e)) ]
            update_loader(loader)
            if verbosity > 0:
                messages.append("Data updated for %s" % app)
            return messages
        else:
            unlock_loader(loader)
            return [ reason ]
    elif verbosity > 0:
        return [ "Data update for %s is locked by another update process/thread since %s" % (app, loader.last_locked.strftime("%d/%m/%Y %H:%M:%D"))]

def get_update_format(app):
    """Return the format specification for the named uploader module."""
    return import_module(app + ".uploader").file_format

def do_upload(app, fh, actual_freq_display=None, verbosity=0):
    """Perform a data upload for the named module

app: The name of the uploader module that will upload the file, or it's
     registered dashboard_loader.models.Uploader object
fh: A file-like object representing the the file to be uploaded.
actual_freq_display: If not None, this is the "actual frequency display"
        value to be passed to the uploader.
verbosity: The verbosity level, 0-3.  Higher numbers = more verbosity.
           (default=0)

Returns a list of messages (strings).

A uploader module is a python package containing a python module uploader.py 
that defines:
    1) groups: A list of names of Django auth groups that have permission to
               run this uploader.  Groups will be created on registration if
               necessary.
    2) file_format: A dictionary describing the file format required by the
               uploader.  This dictionary is not necessarily used by the
               uploader and is intended for documentation purposes.
    3) upload_file: A function that loads data from a provided file_handle.
               Returns a list of logging messages (strings) and take the
               following arguments:
        a) uploader: The dashboard_loader.models.Uploader registration
           object for the uploader module.
        b) fh: A file-like object from which data is to be read.
        c) actual_freq_display: An actual_freq_display value to be 
           written to widgets this uploader is responsible for.  Not
           required, and uploader modules may choose to ignore it.
        d) verbosity: The verbosity level, 0-3.  
           Higher numbers = more verbosity. (default=0)

Uploader modules must be registered with dashboard_loader application. To
register an uploader module, add it to the "INCLUDED_APPS" setting and
run the "register_loaders" django command.
"""
    if isinstance(app, Uploader):
        uploader = app
        app = uploader.app
    else:
        uploader = Uploader.objects.get(app=app)
    upload_file = import_module(app + ".uploader").upload_file
    try:
        messages = upload_file(uploader, fh, actual_freq_display, verbosity)
    except LoaderException, e:
        return [ "Data upload for %s failed: %s" % (app, unicode(e)) ]
    uploader.last_uploaded = datetime.datetime.now(tz)
    uploader.save()
    if verbosity > 0:
        messages.append("Data uploaded for %s" % app)
    return messages

@transaction.atomic
def call_in_transaction(func, *args, **kwargs):
    """Call a function with the supplied arguments, inside a database transaction."""
    return func(*args, **kwargs)

# Not used - only one geo-uploader is currently required and it is accessed directly.
def geo_upload(uploader, filename, url, verbosity=0, **kwargs):
    load_geodata = import_module(uploader + ".geoloader").load_geodata
    try:
        messages = load_geodata(filename, url, verbosity, **kwargs)
        if verbosity > 0:
            messages.append("Geo-data loaded by %s" % uploader)
        return messages
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException(repr(e))

