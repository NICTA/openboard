# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0042_auto_20160321_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetview',
            name='geo_window',
            field=models.ForeignKey(blank=True, to='widget_def.GeoWindow', null=True),
        ),
    ]
