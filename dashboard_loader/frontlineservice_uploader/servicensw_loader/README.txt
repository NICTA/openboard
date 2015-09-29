servicensw_loader

An example dashboard uploader module.

This uploader takes a correctly formatted csv file and loads its content.

To try out this uploader you will need to:

1) Import the relevant widget definitions, etc. In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m servicensw_loader/categories.json servicensw_loader/views.json servicensw_loader/w_svc_calls.json servicensw_loader/w_svc_counters.json servicensw_loader/w_svc_www.json

2) Uncomment servicensw_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Register the uploader:

   python manage.py register_loaders

4) You can now run the uploader with:

   python manage.py upload_data -v3 servicensw_loader servicensw_loader/sample_data.csv "Friday"

   ("Friday" is the actual frequency display text)

Or from the data admin interface.


