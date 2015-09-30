train_interruptions_loader

An example dashboard loader module.

This loader obtains data from an rss feed. It also gives an example
of populating multiple widget definitions within a widget family. (The
"nsw" widget_definition gets all train line interruptions while the "syd"
widget_definition only gets interruptions on Sydney suburban train lines.)

To try out this loader you will need to:

1) Import the relevant widget definitions, etc.  In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m train_interruptions_loader/categories.json train_interruptions_loader/views.json train_interruptions_loader/tlc_std3code.json train_interruptions_loader/tls_*.json train_interruptions_loader/tla_*.json train_interruptions_loader/w_train_service_interrupt.json

2) Uncomment train_interruptions_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Register the loader:

   python manage.py register_loaders

4) You can now run the loader manually with:

   python manage.py update_data -v3 -f train_interruptions_loader

Or from the admin interface.


