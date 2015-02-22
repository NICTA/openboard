# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel_speed_loader', '0003_auto_20150218_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='roadsection',
            name='route_direction',
            field=models.CharField(default='N', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='roadsection',
            unique_together=set([('road', 'sort_order'), ('road', 'origin', 'destination'), ('road', 'label')]),
        ),
    ]
