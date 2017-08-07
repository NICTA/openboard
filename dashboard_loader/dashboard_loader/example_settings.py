#   Copyright 2015, 2017 CSIRO
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

# ALLOWED HOSTS must be set in production, eg:
# ALLOWED_HOSTS = [ 'myserver.com.au', 'myserver_alternatename.com.au' ]
ALLOWED_HOSTS = []

# SECURE_SSL_REDIRECT should be True in production. (Redirects http requests to https)
# SECURE_SSL_REDIRECT = True

INSTALLED_APPS = INSTALLED_APPS + (
        # Your loader/uploader apps here
        )

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

# Absolute local URLs to Login/Logout views.
# LOGIN_URL = "/data/login"
# LOGOUT_URL = "/data/logout"

# Absolute local URL where static resources are mounted.
# STATIC_URL = "/static/"

# Absolute local URL of the main dashboard_loader page, used by admin app.
# ADMIN_SITE_URL = '/data/'

# URL path used by Session Cookie and name of session cookie
# SESSION_COOKIE_PATH = '/data/'
# SESSION_COOKIE_NAME = 'openboard_admin_sessionid'


