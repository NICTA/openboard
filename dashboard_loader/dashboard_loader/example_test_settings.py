"""
Django settings for dashboard_loader project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from dashboard_loader.base_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gsgj5#^65dfy%htgu7*(dfsdw42@dcalppg0)$4kfo0fgougs$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'TEST': {
            'NAME': 'dashboard_test',
        },
        'NAME': 'dashboard_test_stage',
        'USER': 'dashboard_test',
        'PASSWORD': 'testing123',
        'HOST': '127.0.0.1',
    }
}


