"""
Django settings for dashboard_loader project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from dashboard_loader.base_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pho^sdf_%k)t9sh2l#3_2wl^3u5a%ia38^$$a)x-2654j9bmg#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dashboard',
        'USER': 'dashboard',
        'PASSWORD': 'passwd',
        'HOST': '127.0.0.1',
    }
}

# LOGIN_URL = "/data/login"
# LOGOUT_URL = "/data/logout"
# STATIC_URL = "/static/"

# SESSION_COOKIE_PATH = '/data/'

# ADMIN_SITE_URL = '/data/'

