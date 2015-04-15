from dashboard_loader.models import Loader, Uploader

from django.contrib.auth.models import Group

def register(app, refresh_rate=None):
    if refresh_rate is None:
        # uploader
        try:
            l = Uploader.objects.get(app=app)
            result = False
        except Uploader.DoesNotExist:
            l = Uploader(app=app)
            l.save()
            result = True
        p = l.permission()
        groups = get_uploader_groups(app)
        for grp in groups:
            try:
                g = Group.objects.get(name=grp)
            except Group.DoesNotExist:
                g = Group(name=grp).save()
            g.permissions.add(p)
        for grp in Group.objects.all():
            if grp.name not in groups:
                g.permissions.remove(p)
        return result
    else:
        # loader
        old_rate = None
        try:
            l = Loader.objects.get(app=app)
            if l.refresh_rate == refresh_rate:
                return l.refresh_rate
            old_rate = l.refresh_rate
        except Loader.DoesNotExist:
            l = Loader(app=app, suspended=True)
        l.refresh_rate = refresh_rate
        l.save()
        return old_rate

def get_uploader_groups(app):
    _tmp = __import__(app + ".uploader", globals(), locals(),
                    [ "groups", ], -1)
    return _tmp.groups
