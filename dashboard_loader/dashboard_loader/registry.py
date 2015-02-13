from dashboard_loader.models import Loader

def register(app, refresh_rate):
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

