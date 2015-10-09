# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0009_auto_20150610_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='unit_suffix',
            field=models.CharField(max_length=b'40', null=True, blank=True),
        ),
    ]
