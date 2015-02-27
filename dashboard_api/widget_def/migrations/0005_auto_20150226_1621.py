# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0004_auto_20150225_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='hyperlinkable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm'), (7, b'event_list')]),
            preserve_default=True,
        ),
    ]
