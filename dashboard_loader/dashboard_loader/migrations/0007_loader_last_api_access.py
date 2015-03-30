# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_loader', '0006_auto_20150323_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='loader',
            name='last_api_access',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
