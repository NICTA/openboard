# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0031_auto_20150902_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiledefinition',
            name='geo_datasets',
            field=models.ManyToManyField(to='widget_def.GeoDataset', blank=True),
        ),
    ]
