rfs_loader

An example dashboard loader module.

This loader obtains data from an XML feed.  Note that the relevant feed
is only published during the NSW bushfire season and the start and end of
the bushfire season is determined on an ad hoc basis year by year.

To try out this loader you will need to:

1) Import the relevant widget definitions, etc.  In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m rfs_loader/categories.json rfs_loader/views.json rfs_loader/tlc_fire_danger.json rfs_loader/w_fire.json

2) Uncomment rfs_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Register the loader:

   python manage.py register_loaders

4) You can now run the loader manually with:

   python manage.py update_data -v3 -f rfs_loader

Or from the admin interface.


