# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0040_statistic_rotates'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='editable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
