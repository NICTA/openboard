from dashboard_loader.registry import register
from dashboard_loader.models import Loader, Uploader
from django.apps import apps

def register_loaders(verbosity, logger):
    registered_app_loaders = []
    registered_app_uploaders = []
    for app in apps.get_app_configs():
        if verbosity >= 3:
            print >> logger, "Checking app %s" % app.name
        try:
            _tmp = __import__(app.name + '.loader', globals(), locals(), ['refresh_rate',], -1)
            refresh_rate = _tmp.refresh_rate
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
        except (ImportError, AttributeError):
            if verbosity >=2:
                print >> logger, "App %s is not a Loader" % app.name
        try:
            _tmp = __import__(app.name + '.uploader', globals(), locals(),
                            ['upload_file', 'file_format', 'groups'], -1)
            upload_file = _tmp.upload_file
            file_format = _tmp.file_format
            new = register(app.name)
            registered_app_uploaders.append(app.name)
            if new:
                if verbosity > 0:
                    print >> logger, "App %s uploader registered" % app.name
            else:
                if verbosity >= 3:
                    print >> logger, "App %s uploader already registered" % app.name
        except (ImportError, AttributeError):
            if verbosity >=2:
                print >> logger, "App %s is not an Uploader" % app.name
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
