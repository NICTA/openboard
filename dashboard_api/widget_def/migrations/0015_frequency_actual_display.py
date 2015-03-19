# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0014_frequency_display_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='frequency',
            name='actual_display',
            field=models.CharField(default='Real time', unique=True, max_length=60),
            preserve_default=False,
        ),
    ]
