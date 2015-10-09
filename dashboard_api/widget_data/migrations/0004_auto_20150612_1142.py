# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0003_auto_20150611_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticlistitem',
            name='datetime_key',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='statisticlistitem',
            name='datetime_keylevel',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, b'second'), (2, b'minute'), (3, b'hour'), (4, b'day'), (5, b'month'), (6, b'quarter'), (7, b'year')]),
        ),
    ]
