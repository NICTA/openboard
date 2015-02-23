# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_loader', '0003_loader_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='loader',
            name='last_run',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
