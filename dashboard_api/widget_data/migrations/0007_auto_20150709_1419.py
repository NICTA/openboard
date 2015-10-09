# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0006_auto_20150615_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='graphdata',
            options={'ordering': ('graph', 'cluster', 'dataset', 'horiz_numericval', 'horiz_dateval', 'horiz_timeval')},
        ),
    ]
