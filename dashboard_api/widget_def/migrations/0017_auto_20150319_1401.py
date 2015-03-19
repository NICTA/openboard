# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0016_auto_20150318_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_location',
            field=models.ForeignKey(default=3, to='widget_def.Location'),
            preserve_default=False,
        ),
    ]
