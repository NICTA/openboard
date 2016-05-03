# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0050_auto_20160329_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewtype',
            name='show_siblings',
            field=models.BooleanField(default=False),
        ),
    ]
