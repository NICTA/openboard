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

import os
import pytz
import decimal
import datetime
import thread

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group

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

class Uploader(models.Model):
    app = models.CharField(max_length=80, unique=True)
    last_uploaded = models.DateTimeField(null=True, blank=True)
    def permission_name(self):
        return "upload_%s" % self.app
    def permission_label(self):
        p = self.permission()
        return "%s.%s" % (p.content_type.app_label, p.codename)
    def permission(self, log=None):
        ct = ContentType.objects.get_for_model(self)
        try:
            p = Permission.objects.get(content_type=ct, 
                            codename=self.permission_name())
        except Permission.DoesNotExist:
            p = Permission(content_type=ct, codename=self.permission_name(),
                    name="upload data files for %s" % self.app)
            p.save()
            if log:
                    print >> log, "Created uploader permission for %s" % self.app
        return p
    def __unicode__(self):
        if self.last_uploaded:
            return "%s last uploaded %s" % (self.app, self.last_loaded.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            return "%s (no data uploaded)" % self.app

