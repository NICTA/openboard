Openboard
==============

The backend component of a flexible configuration-driven dashboard platform.

The API used for communication between the front and back ends is documented in
API Specification included in the root directory of this release.

Dependencies
============

* Django 1.8  (http://www.djangoproject.com)

  An open source MVC based web application framework written in Python.

  I have been using 1.8.x, which is the most recent major release,
  but I believe the code should work ok under 1.7.x.

  Note that Django 1.8 requires Python 2.7

* django-cors-headers  (https://github.com/ottoyiu/django-cors-headers)

  An open source Django middleware app providing 
  Cross Origin Resource Scripting (CORS) support.

* postgresql (and postGIS) (http://postgresql.org and http://postgis.net)

  For Database access and Geospatial support.

* pytz  (https://pypi.python.org/pypi/pytz/)

  Python Timezone definitions. (open source)

* xlrd  (http://www.python-excel.org)

  Python package for reading xls spreadsheets (open source)

* openpyxl  (http://www.python-excel.org)

  Python package for reading xlsx spreadsheets (open source)

* celery (http://www.celeryproject.org/)

  Open source python distributed task queue system, with django integration.

  NB: Install via easy_install/pip, not apt

* rabbitmq  (https://www.rabbitmq.com/)

  Open source message queue system.  Acts as a message broker
  for celery.  N.B. Any other message broker system supported
  by celery could be used instead of RabbitMQ.

  NB: In Ubuntu, Install librabbitmq1. Do NOT install python-librabbitmq !!

Quick Tour of the Source Code
=============================

The Dashboard Server consists of two Django projects, sharing some apps,
and some example celery configuration files.

dashboard_api
--------------

This project consists of three apps (widget_def, widget_data and the
project-app dashboard_api).

widget_def: Contains the tables for the widget definitions and associated
metadata, and the associated API view methods.

widget_data: Contains the tables containing the actual data for the widgets,
and the API views for accessing it.

dashboard_api: Contains some manage.py commands for supporting the project,
as well as the project settings, urls.py, and other shared resources

### manage.py commands

* cleanup_widget_perms 

  Ensures correct widget permissions exist for all defined 
  widget families.

* export_categories
* export_views
* export_colourmap
* export_geowindow
* export_geocolourscale
* export_geodataset
* export_trafficlightscale
* export_trafficlightstrategy
* export_trafficlightautomation
* export_iconlibrary
* export_widget

  Export various metadata definitions as json files.

* import_data

  Import metadata definition json files, as exported by the
  export commands above.
	
* export_widget_data
  Export the data for a widget as a json file.

* migrate_raw_to_geo

  Generates geo dataset metadata json based on raw dataset metadata json.
	
Use manage.py help for more information.	

dashboard_loader
----------------

This project consists of one core app (dashboard_loader) to which developers
can add additional loader (or uploader) apps, as described below. The loader
and uploader apps make use of the dashboard loader API which is defined (and
documented) in dashboard_loader.loader_utils.  Some example loader and uploader
apps are provided.

Django Admin pages are provided for maintaining widget definitions and
associated metadata, as well as custom maintenance views for manually 
maintaining widget data and user accounts and permissions.

### Loader Apps

A loader app is an app included in the dashboard_loader project that has
a loader.py file and/or an uploader.py file.  The loader app may define it's
own models (and optionally register them with the admin site) as needed.

An loader.py file must define:

* refresh_rate

  A integer variable specifying how often the loader should
  be called by celery (in seconds).

* update_data()

  A function taking dashboard_loader.models.Loader object as
  it's first parameter, and an optional integer verbosity level
  (as used by manage.py commands).

  Typically accesses an external API and updates the data 
  for one or more widgets.

  Returns a list of log message strings (which should always be
  empty if verbosity is 0.	

  On error raises dashboard_loader.loader_utils.LoaderException.

```
def update_data(loader, verbosity=0):
	return []
```

An uploader.py file must define:

* groups

  A list or tuple of auth.group names.  All named groups have
  permission to upload data for this uploader.

* file_format

  A structured dictionary outlining the file format for the
  uploaded data file (csv or xls).  See 
  frontlineservice_uploader/uploader.py for an example.

* upload_file()

  A function taking the following arguments:

  * uploader 

    A dashboard_loader.models.Uploader instance.

  * fh 

    A file handle to the uploaded data file.

  * actual_freq_display

    An optional value to update the actual_frequency_display value to, 
    for the affected widgets.

  * verbosity

    An optional logging verbosity, as used by manage.py commands.

  Reads an uploaded datafile of a defined format and updates
  one or more widgets with its contents.

  Returns a list of log message strings (which should always be
  empty if verbosity is 0.	

  On error raises dashboard_loader.loader_utils.LoaderException.

```
def upload_file(uploader, fh, actual_freq_display=None, 
		verbosity=0):
	return []
```

### manage.py commands

(All the manage.py commands described above for the dashboard_api
project are also available from dashboard_loader.)

* register_loaders

  Scans all included apps for uploader.py and loader.py files,
  and updates the relevant Loader and Uploader records in the 
  database.

* update_data

  Manually run a particular loader.

* upload_data

  Manually run a particular uploader.

* upload_geodata

  Upload a geodataset from a shapefile or geojson file.

* import_widget_data

  Import widget data from a json file, as created by the
  export_widget_data command described above.
	
* testall

  Run Django tests on all dashboard apps. Note that to create
  a postgis enabled test database the test user will need
  superuser database access.  Therefore tests should never be
  run in a production environment for security reasons.

Use manage.py help for more information.	

celery_init
-----------

Some example init scripts and config files for celeryd and celerybeat.

Assumes Ubuntu Linux, but will need some fine tuning for any given 
installation.

Getting Started
===============

This is a list of things you will need to do to get things working.

It is probably incomplete.

1. Install dependencies and install source code.

2. Create a postgresql database.  Enable postgis extensions with:

   ```
   create extension postgis;
   ```

3. Copy example_settings.py to settings.py and customise for your local 
   environment.  (for both dashboard_api and dashboard_loader)

4. Copy the contents of celery_init/default to /etc/default and the contents
   of celery_init/init.d to /etc/init.d and edit for your local
   environment.

5. Run python manage.py migrate in dashboard_api, then in dashboard_loader.

6. Edit wsgi.py and setup apache OR use manage.py runserver to run instances of
   both projects.

7. Start your celery and celerybeat instances.

8. Create widget definitions and metadata through the admin interface, or use 
   the import_data to command to import someone else's metadata.

9. Manually populate the data for your widgets through the maintenance screen.

10. Create loader/uploader apps and add them to the INCLUDED_APPS for 
    dashboard_loader.  (And reload apache if necessary).

11. Run manage.py migrate to create any working storage database tables
    used by the included loader and uploader modules.

12. Run manage.py register_loaders to register the loaders and uploaders.  
    Loaders are created in a suspended state.

13. Got the Loader admin page, and manually run or unsuspend the new loaders.

