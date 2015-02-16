from __future__ import absolute_import

from celery import shared_task

from dashboard_loader.loader_utils import do_update
from dashboard_loader.models import Loader

@shared_task
def update_app_data(app):
    return do_update(app)

@shared_task
def update_all_apps():
    updates_queued = 0
    loaders = Loader.objects.all()
    for loader in loaders:
        if not loader.reason_to_not_run():
            update_app_data.delay(loader.app)
            updates_queued += 1
    return updates_queued

