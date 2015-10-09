# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0014_widgetdefinition_deexpansion_hint'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdisplayoptions',
            name='rotates',
            field=models.BooleanField(default=False),
        ),
    ]
