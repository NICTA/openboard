from __future__ import absolute_import

import os
import sys

from celery import Celery

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'dashboard_api'))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_loader.settings')

from django.conf import settings

app = Celery('dashboard_loader')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    return('Request: {0!r}'.format(self.request))

