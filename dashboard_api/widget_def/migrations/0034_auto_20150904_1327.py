# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0033_auto_20150903_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='geodataset',
            name='ext_type',
            field=models.CharField(help_text=b"For External GeoDatasets only - used as 'type' field in Terria catalog.", max_length=80, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='geodataset',
            name='ext_url',
            field=models.URLField(help_text=b'For External GeoDatasets only', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='geopropertydefinition',
            name='predefined_geom_property',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='geodataset',
            name='geom_type',
            field=models.SmallIntegerField(choices=[(1, b'point'), (2, b'line'), (3, b'polygon'), (4, b'multi-point'), (5, b'multi-line'), (6, b'multi-polygon'), (7, b'predefined'), (8, b'external')]),
        ),
    ]
