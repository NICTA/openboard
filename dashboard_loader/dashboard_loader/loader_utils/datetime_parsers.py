import datetime

from interface import tz, LoaderException

def parse_date(d):
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
    if t is None:
        return None
    elif isinstance(t, datetime.time):
        return t
    elif isinstance(t, datetime.datetime):
        return t.time()
    for fmt in ("%H:%M:%S", "%H-%M-%S", "%H:%M", "%H-%M"):
        try:
            dt = datetime.datetime.strptime(t, "%H:%M:%S")
            return dt.time()
        except ValueError:
            pass
        except TypeError:
            raise LoaderException("Cannot parse t as a time: %s" % repr(t))
    raise LoaderException("Not a valid time string: %s" % repr(t))

def parse_datetime(dt):
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

