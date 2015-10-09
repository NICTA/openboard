traffic_incident_loader

An example dashboard loader module.

This loader obtains data from an json feed. 

To try out this loader you will need to:

1) Import the relevant widget definitions, etc.  In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m traffic_incident_loader/categories.json traffic_incident_loader/views.json traffic_incident_loader/tlc_std3code.json traffic_incident_loader/w_traffic_incidents.json

2) Uncomment traffic_incident_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Register the loader:

   python manage.py register_loaders

4) You can now run the loader manually with:

   python manage.py update_data -v3 -f traffic_incident_loader

Or from the admin interface.


