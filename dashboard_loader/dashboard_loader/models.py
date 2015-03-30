import os
import pytz
import decimal
import datetime
import thread

from django.db import models
from django.conf import settings

class Loader(models.Model):
    app = models.CharField(max_length=80, unique=True)
    refresh_rate=models.IntegerField()
    suspended=models.BooleanField(default=False)
    last_run=models.DateTimeField(null=True, blank=True)
    last_loaded=models.DateTimeField(null=True, blank=True)
    last_locked=models.DateTimeField(null=True, blank=True)
    locked_by_process=models.IntegerField(null=True, blank=True)
    locked_by_thread=models.DecimalField(max_digits=19, decimal_places=0,null=True, blank=True)
    last_api_access=models.DateTimeField(null=True, blank=True)
    def reason_to_not_run(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        if self.suspended:
            return u'Loader %s is suspended' % self.app
        if self.last_loaded:
            now = datetime.datetime.now(tz)
            diff = now - self.last_loaded
            if diff.total_seconds() < self.refresh_rate:
                return "Loader %s not due for refresh until %s" % (self.app, (self.last_loaded + datetime.timedelta(seconds=self.refresh_rate)).astimezone(tz).strftime("%d/%m/%Y %H:%M:%S"))
            if self.last_run and self.last_run > self.last_loaded:
                now = datetime.datetime.now(tz)
                diff = now - self.last_run
                failure_recovery = int(self.refresh_rate * 0.2)
                if diff.total_seconds() < failure_recovery:
                    return "Last attempt to run loader %s failed. Waiting to retry at %s" % (self.app, (self.last_run + datetime.timedelta(seconds=failure_recovery)).astimezone(tz).strftime("%d/%m/%Y %H:%M:%S"))
        return None
    def lock(self):
        self.locked_by_process = os.getpid()
        self.locked_by_thread = decimal.Decimal(thread.get_ident())
        self.last_locked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    def locked_by_me(self):
        if self.locked_by_process and self.locked_by_process == os.getpid() and self.locked_by_thread == decimal.Decimal(thread.get_ident()): 
            return True
        else:
            return False
    def __unicode__(self):
        if self.last_loaded:
            return "%s last loaded %s" % (self.app, self.last_loaded.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            return "%s (no data loaded)" % self.app

