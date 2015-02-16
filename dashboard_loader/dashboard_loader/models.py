import os
import pytz
import datetime

from django.db import models
from django.conf import settings

class Loader(models.Model):
    app = models.CharField(max_length=80, unique=True)
    refresh_rate=models.IntegerField()
    suspended=models.BooleanField(default=False)
    last_loaded=models.DateTimeField(null=True, blank=True)
    locked_by=models.IntegerField(null=True, blank=True)
    def reason_to_not_run(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        if self.suspended:
            return u'Loader %s is suspended' % self.app
        if self.last_loaded:
            now = datetime.datetime.now(tz)
            diff = now - self.last_loaded
            if diff.total_seconds() < self.refresh_rate:
                return "Loader %s not due for refresh until %s" % (self.app, (self.last_loaded + datetime.timedelta(seconds=self.refresh_rate)).astimezone(tz).strftime("%d/%m/%Y %H:%M:%S")) 
        return None
    def locked_by_me(self):
        if self.locked_by and self.locked_by == os.getpid():
            return True
        else:
            return False
    def __unicode__(self):
        if self.last_loaded:
            return "%s last loaded %s" % (self.app, self.last_loaded.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            return "%s (no data loaded)" % self.app

