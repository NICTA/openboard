"""
Django settings for dashboard_api project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Override in local settings.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    )
TEMPLATE_DIRS = (
)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'dashboard_api',
    'widget_def',
    'widget_data',
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dashboard_api.urls'

WSGI_APPLICATION = 'dashboard_api.wsgi.application'

# CORS

CORS_ORIGIN_ALLOW_ALL = True

# If not allowing all, use whitelist:
# CORS_ORIGIN_WHITELIST = ('hostname.domain.com', 'foo.bar.com.au',)
# or regex_whitelists:
# CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://)?(\w+\.)?google\.com$', )

# Can restrict methods.  Default is all methods.
# CORS_ALLOW_METHODS= ('GET', )

# CORS_ALLOW_CREDENTIALS: specify whether or not cookies are allowed to be included in cross-site HTTP requests (CORS).  Default: False
# CORS_ALLOW_CREDENTIALS = True

# See https://github.com/ottoyiu/django-cors-headers/blob/master/README.md
# for other CORS options.

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKE_AGE = 24*60*60*2

SESSION_COOKIE_HTTPONLY = False

