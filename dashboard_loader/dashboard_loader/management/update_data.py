import datetime
import pytz

from django.conf import settings

from dashboard_loader.loader_utils import update_loader, lock_update

def update(app, verbosity=0, force=False):
    tz = pytz.timezone(settings.TIME_ZONE)
    if app.suspended and not force:
        if verbosity >= 3:
            return ["Loader %s is suspended" % app.app, ]
        return []
    if app.last_loaded:
        now = datetime.datetime.now(tz)
        diff = now - app.last_loaded
        if diff.total_seconds() < app.refresh_rate and not force:
            if verbosity >= 3:
                return ["Loader %s not due for refresh until %s" % (app.app, (app.last_loaded + datetime.timedelta(seconds=app.refresh_rate)).astimezone(tz).strftime("%d/%m/%Y %H:%M:%S")) ]
            return []
    _tmp = __import__(app.app + ".loader", globals(), locals(), ["update_data",], -1)
    update_data = _tmp.update_data
    if lock_update(app):
        messages = update_data(app, verbosity=verbosity)
        update_loader(app)
        if verbosity > 0:
            messages.append("Data updated for %s" % app.app)
        return messages
    elif verbosity > 0:
        return [ "Data update for %s is locked by another update process" % app.app]

