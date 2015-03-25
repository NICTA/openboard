# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0036_auto_20150325_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (10, b'single_list_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid'), (11, b'newsfeed')]),
            preserve_default=True,
        ),
    ]
