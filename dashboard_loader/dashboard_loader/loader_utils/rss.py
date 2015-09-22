import urllib
import xml.etree.ElementTree as ET
from interface import LoaderException

def load_rss(url, process_item, environment={}, verbosity=0):
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

