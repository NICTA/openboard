# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0039_auto_20150331_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='rotates',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
