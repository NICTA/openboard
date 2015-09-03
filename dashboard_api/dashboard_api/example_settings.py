"""
Django settings for dashboard_api project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from dashboard_api.base_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k_&ywy8shj9!_zsyvlr1+z25z_8e9_t1m1c+qi9lp3tqn^a-fo'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'TEST': {
            'NAME': 'dashboard_test',
        },
        'NAME': 'dashboard',
        'USER': 'dashboard',
        'PASSWORD': 'passwd',
        'HOST': '127.0.0.1',
    },
}



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# CORS

CORS_ORIGIN_ALLOW_ALL = True

# If not allowing all, use whitelist:
# CORS_ORIGIN_WHITELIST = ('hostname.domain.com', 'foo.bar.com.au',)
# or regex_whitelists:
# CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://)?(\w+\.)?google\.com$', )

# Can restrict methods.  Default is all methods.
# CORS_ALLOW_METHODS= ('GET', )

# CORS_ALLOW_CREDENTIALS: specify whether or not cookies are allowed to be included in cross-site HTTP requests (CORS).  Default: False
CORS_ALLOW_CREDENTIALS = True

# See https://github.com/ottoyiu/django-cors-headers/blob/master/README.md
# for other CORS options.

# Terria integration settings

TERRIA_TOP_LEVEL_MENU = "My Dashboard Datasets"
TERRIA_LAYER_OPACITY = 0.9
TERRIA_BASE_MAP_NAME = "Positron (Light)"
TERRIA_CORS_DOMAINS = [ "www.yourfrontend.website.url", ]
TERRIA_API_BASE = [ "https://www.yourfrontend.website.url", ]

# Allow Public access to API (for themes that are marked as not requiring auth
PUBLIC_API_ACCESS = False
