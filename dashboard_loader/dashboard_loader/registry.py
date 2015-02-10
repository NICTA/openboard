from dashboard_loader.models import Loader

def register(app, refresh_rate):
    try:
        l = Loader.objects.get(app=app)
        if l.refresh_rate == refresh_rate:
            return
    except Loader.DoesNotExist:
        l = Loader(app=app)
    l.refresh_rate = refresh_rate
    l.save()

