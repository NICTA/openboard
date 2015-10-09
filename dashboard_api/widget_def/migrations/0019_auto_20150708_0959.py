# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0018_auto_20150625_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphdefinition',
            name='horiz_axis_type',
            field=models.SmallIntegerField(default=0, choices=[(0, b'-'), (1, b'numeric'), (2, b'date'), (3, b'time'), (4, b'datetime')]),
        ),
    ]
