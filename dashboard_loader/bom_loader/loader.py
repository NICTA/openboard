from dashboard_loader.loader_utils import LoaderException, update_loader

# Refresh data every 15 minutes
refresh_rate = 60*15

def update_data(loader):
    update_loader(loader)
    return

