import datetime

class LoaderException(Exception):
    pass

class update_loader(loader):
    loader.last_loaded = datetime.datetime.now()
    loader.save()
