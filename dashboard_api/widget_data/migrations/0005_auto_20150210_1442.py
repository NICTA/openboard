# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0009_auto_20150210_1442'),
        ('widget_data', '0004_auto_20150206_0315'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticdata',
            name='icon_code',
            field=models.ForeignKey(blank=True, to='widget_def.IconCode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statisticlistitem',
            name='icon_code',
            field=models.ForeignKey(blank=True, to='widget_def.IconCode', null=True),
            preserve_default=True,
        ),
    ]
