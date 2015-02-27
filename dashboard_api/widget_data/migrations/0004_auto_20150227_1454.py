# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0003_auto_20150226_1651'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statisticlistitem',
            options={'ordering': ('statistic', 'datekey', 'sort_order')},
        ),
    ]
