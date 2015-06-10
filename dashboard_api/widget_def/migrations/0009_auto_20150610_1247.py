# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0008_auto_20150610_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widgetdefinition',
            name='expansion_hint',
            field=models.CharField(max_length=80, null=True, blank=True),
        ),
    ]
