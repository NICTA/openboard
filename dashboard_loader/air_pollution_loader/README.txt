air_pollution_loader

An example dashboard loader module.

This loader obtains data by scraping a web-page.  This is the least-preferred
method of automatically obtaining data.  Not only does it require the most
work, but it typically requires regular maintenance when the source web-page
undergoes unexpected and unadvertised design changes.  (Indeed it is quite
possible that this example code no longer works due to changes at the source
web-page since the code was written - caveat emptor!)

To try out this loader you will need to:

1) Import the relevant widget definitions, etc.  In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m air_pollution_loader/categories.json air_pollution_loader/views.json air_pollution_loader/tlc_air_pollution_scale.json air_pollution_loader/w_air_pollution.json

2) Uncomment air_pollution_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Register the loader:

   python manage.py register_loaders

4) You can now run the loader manually with:

   python manage.py update_data -v3 -f air_pollution_loader

Or from the admin interface.


