# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0026_auto_20150828_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geodataset',
            name='tiles',
        ),
        migrations.AddField(
            model_name='geodataset',
            name='label',
            field=models.CharField(default='Default Label', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tiledefinition',
            name='geo_datasets',
            field=models.ManyToManyField(to='widget_def.GeoDataset'),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (18, b'text_template'), (10, b'single_list_stat'), (15, b'multi_list_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (13, b'graph_single_stat'), (7, b'map'), (9, b'grid'), (14, b'grid_single_stat'), (8, b'calendar'), (17, b'time_line'), (11, b'newsfeed'), (12, b'news_ticker'), (16, b'tag_cloud')]),
        ),
    ]
