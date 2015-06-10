# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0006_auto_20150610_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widgetfamily',
            name='subtitle',
            field=models.CharField(max_length=120, null=True, blank=True),
        ),
    ]
