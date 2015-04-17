# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0042_auto_20150415_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (8, b'long_string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (9, b'long_string_list'), (6, b'am_pm'), (7, b'event_list')]),
            preserve_default=True,
        ),
    ]
