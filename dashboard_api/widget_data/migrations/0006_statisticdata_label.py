# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0005_auto_20150210_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticdata',
            name='label',
            field=models.CharField(max_length=80, null=True, blank=True),
            preserve_default=True,
        ),
    ]
