# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_loader', '0004_loader_last_run'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loader',
            old_name='locked_by',
            new_name='locked_by_process',
        ),
        migrations.AddField(
            model_name='loader',
            name='last_locked',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loader',
            name='locked_by_thread',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
