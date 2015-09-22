import datetime
import pytz
import os
import thread

from django.conf import settings
from django.db import transaction

from dashboard_loader.models import Loader, Uploader

tz = pytz.timezone(settings.TIME_ZONE)

class LoaderException(Exception):
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
    _tmp = __import__(app + ".loader", globals(), locals(), ["update_data",], -1)
    update_data = _tmp.update_data
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
    _tmp = __import__(app + ".uploader", globals(), locals(), ["file_format",], -1)
    return _tmp.file_format

def do_upload(app, fh, actual_freq_display=None, verbosity=0):
    if isinstance(app, Uploader):
        uploader = app
        app = uploader.app
    else:
        uploader = Uploader.objects.get(app=app)
    _tmp = __import__(app + ".uploader", globals(), locals(), 
                        ["upload_file", ], -1)
    upload_file = _tmp.upload_file
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
    return func(*args, **kwargs)

# Not used - only one geo-uploader is currently required and it is accessed directly.
def geo_upload(uploader, filename, url, verbosity=0, **kwargs):
    _tmp = __import__(uploader + ".geoloader", globals(), locals(), ["load_geodata",], -1)
    load_geodata = _tmp.load_geodata
    try:
        messages = load_geodata(filename, url, verbosity, **kwargs)
        if verbosity > 0:
            messages.append("Geo-data loaded by %s" % uploader)
        return messages
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException(repr(e))

