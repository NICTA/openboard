# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0047_auto_20160323_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='default_frequency_text',
            field=models.CharField(default='-', max_length=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='label',
            field=models.CharField(default='-', max_length=128),
            preserve_default=False,
        ),
    ]
