import decimal
import random
import httplib
import oauth2 as oauth
import json

from django.conf import settings

from dashboard_loader.loader_utils import clear_statistic_list, add_statistic_list_item, call_in_transaction, LoaderException

# Refresh every 40 seconds
refresh_rate = 40

# Function called when the loader is run.
def update_data(loader, verbosity=0):
    messages = []
    try:
        messages = call_in_transaction(get_tweets,messages, verbosity)
    except LoaderException, e:
        raise e
    except Exception, e:
        print unicode(e)
        raise LoaderException(unicode(e))
    return messages

# Access Twitter API and dowload Tweets.
def get_tweets(messages, verbosity):
    # Connect to Twitter API with OAuth2
    consumer = oauth.Consumer(key=settings.TWITTER_API_KEY, 
                    secret=settings.TWITTER_API_SECRET)
    token = oauth.Token(key=settings.TWITTER_ACCESS_TOKEN,
                    secret=settings.TWITTER_ACCESS_TOKEN_SECRET)
    client = oauth.Client(consumer, token)
    # Get list of recent tweets
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    resp, content = client.request(url, method="GET")
    data = json.loads(content)
    tweets = []
    for d in data:
        tweets.append({"user": d["user"]["name"], "tuser": "@" + d["user"]["screen_name"], "tweet": d["text"]})
    # Load 5 random tweets into widget
    random.shuffle(tweets)
    clear_statistic_list("tweets", "nsw", "rt", "tweets")
    sort_order = 1
    for t in tweets:
        add_statistic_list_item("tweets", "nsw", "rt", "tweets",
                        t["tweet"], sort_order=sort_order,
                        label=t["tuser"])
        if sort_order >= 5:
            break
        sort_order += 1
    if verbosity > 1:
        messages.append("Stored %d tweets" % sort_order)
    return messages


