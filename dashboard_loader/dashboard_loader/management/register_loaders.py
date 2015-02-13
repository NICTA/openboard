from dashboard_loader.registry import register
from dashboard_loader.models import Loader
from django.apps import apps

def register_loaders(verbosity, logger):
    registered_apps = []
    for app in apps.get_app_configs():
        if verbosity >= 3:
            print >> logger, "Attempting to load app %s" % app.name
        try:
            _tmp = __import__(app.name + '.loader', globals(), locals(), ['refresh_rate',], -1)
            refresh_rate = _tmp.refresh_rate
            old_rate = register(app.name, refresh_rate)
            registered_apps.append(app.name)
            if old_rate is None:
                if verbosity > 0:
                    print >> logger, "App %s registered (suspended)" % app.name
            elif old_rate == refresh_rate:
                if verbosity >= 2:
                    print >> logger, "App %s already registered" % app.name
            else:
                if verbosity > 0:
                    print >> logger, "Refresh rate for app %s updated from %s to %s" % (app.name, old_rate, refresh_rate)
        except ImportError:
            if verbosity >=2:
                print >> logger, "App %s is not a Loader" % app.name

    for l in Loader.objects.all():
        if l.app not in registered_apps:
            l.delete()
            if verbosity > 0:
                print >> logger, "App %s deregistered" % l.app
    return
