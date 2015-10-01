twitter_loader

An example dashboard loader module.

This loader obtains data from a json API secured with OAuth2 (Twitter).
The loader connects to Twitter as a configured Twitter user and randomly
selects 5 recent tweets from the Twitter feeds that the configured Twitter
user follows.

To try out this loader you will need to:

1) Import the relevant widget definitions, etc.  In the dashboard_loader
   directory (i.e. the parent directory to the directory containing this README
   file), run the following command:

python manage.py import_data -m twitter_loader/categories.json twitter_loader/views.json twitter_loader/w_tweets.json

2) Uncomment twitter_loader in the INSTALLED_APPS list in 
   ../dashboard_loader/base_settings.py

3) Create a dedicated twitter account and use it to follow the twitter feeds 
	you want to appear in the widget. 

4) Populate the following settings in settings.py with the values provided to 
	you by Twitter for the dedicated Twitter account.

	TWITTER_API_KEY
	TWITTER_API_SECRET
	TWITTER_ACCESS_TOKEN
	TWITTER_ACCESS_TOKEN_SECRET

5) Register the loader:

   python manage.py register_loaders

6) You can now run the loader manually with:

   python manage.py update_data -v3 -f twitter_loader

Or from the admin interface.

