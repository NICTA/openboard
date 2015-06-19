# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0012_auto_20150615_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='aspect',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='graphdisplayoptions',
            name='lines',
            field=models.SmallIntegerField(default=0, choices=[(0, b'none'), (1, b'straight'), (2, b'bezier')]),
        ),
    ]
