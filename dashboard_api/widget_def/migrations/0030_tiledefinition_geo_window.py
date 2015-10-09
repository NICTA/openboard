# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0029_auto_20150901_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='geo_window',
            field=models.ForeignKey(blank=True, to='widget_def.GeoWindow', null=True),
        ),
    ]
