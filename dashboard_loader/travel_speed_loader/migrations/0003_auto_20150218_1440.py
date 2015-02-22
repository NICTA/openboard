# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel_speed_loader', '0002_auto_20150218_1421'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roadsection',
            options={'ordering': ('road', 'sort_order')},
        ),
        migrations.AddField(
            model_name='roadsection',
            name='sort_order',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
