# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0013_auto_20150317_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='frequency',
            name='display_mode',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
