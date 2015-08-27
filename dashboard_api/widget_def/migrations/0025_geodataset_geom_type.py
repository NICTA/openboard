# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0024_auto_20150827_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='geodataset',
            name='geom_type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'point'), (2, b'line'), (3, b'polygon'), (4, b'multi-point'), (5, b'multi-line'), (6, b'multi-polygon')]),
            preserve_default=False,
        ),
    ]
