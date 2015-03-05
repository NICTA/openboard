# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0008_auto_20150304_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdataset',
            name='use_secondary_numeric_axis',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='graphdefinition',
            name='secondary_numeric_axis_always_show_zero',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='graphdefinition',
            name='secondary_numeric_axis_label',
            field=models.CharField(max_length=120, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='graphdefinition',
            name='use_secondary_numeric_axis',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
