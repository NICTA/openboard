# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0005_auto_20150615_1114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statisticlistitem',
            options={'ordering': ('statistic', 'datetime_key', '-datetime_keylevel', 'sort_order')},
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitem',
            unique_together=set([('statistic', 'datetime_key', 'datetime_keylevel', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='statisticlistitem',
            name='datekey',
        ),
    ]
