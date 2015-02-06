# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0007_auto_20150204_0406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tiledefinition',
            name='am_pm',
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm')]),
            preserve_default=True,
        ),
    ]
