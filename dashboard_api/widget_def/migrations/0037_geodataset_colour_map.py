# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0036_auto_20150910_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='geodataset',
            name='colour_map',
            field=models.ForeignKey(blank=True, to='widget_def.GeoColourScale', null=True),
        ),
    ]
