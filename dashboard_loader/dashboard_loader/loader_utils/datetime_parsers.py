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

import datetime

from interface import tz, LoaderException

def parse_date(d):
    """Parse a string into a datetime.date

Supported formats:  YYYY-MM-DD
"""
    if d is None:
        return None
    elif isinstance(d, datetime.date):
        return d
    elif isinstance(d, datetime.date):
        return d.date()
    try:
        dt = datetime.datetime.strptime(d, "%Y-%m-%d")
        return dt.date()
    except ValueError:
        raise LoaderException("Not a valid date string: %s" % repr(d))

def parse_time(t):
    """Parse a string into a datetime.time

Supported formats:  hh:mm:ss
                    hh-mm-ss
                    hh:mm
                    hh-mm
"""
    if t is None:
        return None
    elif isinstance(t, datetime.time):
        return t
    elif isinstance(t, datetime.datetime):
        return t.time()
    for fmt in ("%H:%M:%S", "%H-%M-%S", "%H:%M", "%H-%M"):
        try:
            dt = datetime.datetime.strptime(t, fmt)
            return dt.time()
        except ValueError:
            pass
        except TypeError:
            raise LoaderException("Cannot parse t as a time: %s" % repr(t))
    raise LoaderException("Not a valid time string: %s" % repr(t))

def parse_datetime(dt):
    """Parse a string into a datetime.datetime
(Assume default timezone as per settings file)

Supported formats:  YYYY-MM-DDThh:mm:ss
                    YYYY-MM-DD
                    YYYY
                    DD mmm YYYY hh:mm:ss
                    YYYYQq
"""
    if dt is None:
        return None
    elif isinstance(dt, datetime.date):
        return tz.localize(dt)
    elif isinstance(dt, datetime.date):
        return tz.localize(datetime.datetime.combine(dt, datetime.time()))
    for fmt in ("%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%Y",
                "%d %b %Y %H:%M:%S",
            ):
        try:
            dt = datetime.datetime.strptime(dt, fmt)
            return tz.localize(dt)
        except ValueError:
            pass
    try:    
        dt = datetime.datetime.strptime(dt, "%YQ%m")
        dt = dt.replace(month=(dt.month-1)*3+1)
        return tz.localize(dt)
    except ValueError:
        raise LoaderException("Not a valid date string: %s" % repr(dt))

