# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0017_auto_20150622_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='template',
            field=models.CharField(help_text=b"Reference statistics with '%{statistic_url}", max_length=512, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (18, b'text_template'), (10, b'single_list_stat'), (15, b'multi_list_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (13, b'graph_single_stat'), (9, b'grid'), (14, b'grid_single_stat'), (8, b'calendar'), (17, b'time_line'), (11, b'newsfeed'), (12, b'news_ticker'), (16, b'tag_cloud')]),
        ),
    ]
