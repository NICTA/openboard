from django.db import models

class Loader(models.Model):
    app = models.CharField(max_length=80, unique=True)
    refresh_rate=models.IntegerField()
    suspended=models.BooleanField(default=False)
    last_loaded=models.DateTimeField(null=True, blank=True)
    locked_by=models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        if self.last_loaded:
            return "%s last loaded %s" % (self.app, self.last_loaded.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            return "%s (no data loaded)" % self.app
