#   Copyright 2015 NICTA
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

