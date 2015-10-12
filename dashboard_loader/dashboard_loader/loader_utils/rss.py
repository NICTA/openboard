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

import urllib
import xml.etree.ElementTree as ET
from interface import LoaderException

def load_rss(url, process_item, environment={}, verbosity=0):
    """Utility function for processing RSS feeds with the ElementTree XML API.

url: The url of the RSS feed.
environment: a state object to passed to each call to process_item
verbosity: The verbosity level, 0-3.  Higher numbers = more verbosity.
           (default=0)
process_item: A callback function for processing each rss item. Returns
              a list of logging messages on success or raises a 
              LoaderException on error, and takes the following
              arguments:
        elem: An ElementTree element representing an RSS item.
        environment: The state object.
        verbosity: The verbosity level.

Returns a list of logging messages on success, or raises a LoaderException
on error.
"""
    messages = []
    try:
        response = urllib.urlopen(url) 
        xml = ET.parse(response)
        for elem in xml.getroot()[0]:
            if elem.tag == 'item':
                messages.extend(process_item(elem, environment, verbosity))
        response.close()
    except LoaderException:
        raise
    except Exception, e:
        raise LoaderException("Unexpected error processing RSS feed at %s: (%s)%s",
                            (url, e.__class__.__name__, unicode(e)))
    return messages

