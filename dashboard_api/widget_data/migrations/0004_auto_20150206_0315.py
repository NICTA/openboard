# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0003_auto_20150204_0618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statisticlistitem',
            name='statistic',
            field=models.ForeignKey(to='widget_def.Statistic'),
            preserve_default=True,
        ),
    ]
