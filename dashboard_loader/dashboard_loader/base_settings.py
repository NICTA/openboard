#   Copyright 2015,2016 NICTA
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

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ## Set in local settings file!!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'dashboard_loader',
    'dashboard_api',
    'widget_def.apps.WidgetDefConfig',
    'widget_data',
#    'traffic_incident_loader',
#    'frontlineservice_uploader',
#    'rfs_loader',
#    'train_interruptions_loader',
#    'air_pollution_loader',
#    'twitter_loader',

    'coag_uploader',
    'housing_rentalstress_uploader',
    'housing_homelessness_uploader',
    'housing_indigenous_homeownership_uploader',
    'housing_indigenous_overcrowding_uploader',
    'housing_remote_indigenous_uploader',
    'housing_homelessness_npa_uploader',
    'education_yr12_uploader',
    'education_yr12_2015_uploader',
    'education_naplan_uploader',
    'education_participation_uploader',
    'education_ecenqs_uploader',
    'skills_cert3_uploader',
    'skills_higher_qual_uploader',
    'skills_improved_employment_uploader',
    'health_life_expectancy_uploader',
    'health_diabetes_uploader',
    'disability_labour_participation_uploader',
    'disability_social_participation_uploader',
    'disability_more_assist_uploader',
    'indigenous_child_mortality_uploader',
    'infrastructure_npa_uploader',
    'legal_assistance_total_services_uploader',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dashboard_loader.urls'

WSGI_APPLICATION = 'dashboard_loader.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CELERYBEAT_SCHEDULE = {
    'poll_all_apps': {
            'task': 'dashboard_loader.tasks.update_all_apps',
            'schedule': datetime.timedelta(seconds=1),
            'args': (),
    },
}

# Allow tasks to run for up to 12 hours - Is there a smarter way
# to load the GTFS static data?
CELERYD_TASK_TIME_LIMIT = 60 * 60 * 12

LOGIN_URL="/login"
LOGOUT="/logout"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
LOCALROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."

STATIC_ROOT = LOCALROOT + '/static'
STATICFILES_DIRS = []
     
STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        )
STATIC_URL = '/static/'

SESSION_COOKIE_PATH = '/'

ADMIN_SITE_URL = "/"

TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                "context_processors":  [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                ],
            }
        },
]

# TWITTER_API_KEY="KEY..."
# TWITTER_API_SECRET="SECRET..."
# TWITTER_ACCESS_TOKEN="TOKEN..."
# TWITTER_ACCESS_TOKEN_SECRET="TOKEN..."

