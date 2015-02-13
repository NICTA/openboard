# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_loader', '0002_loader_locked_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='loader',
            name='suspended',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
