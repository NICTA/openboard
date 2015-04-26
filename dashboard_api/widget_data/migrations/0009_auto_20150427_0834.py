# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0008_auto_20150413_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statisticdata',
            name='statistic',
            field=models.OneToOneField(to='widget_def.Statistic'),
        ),
        migrations.AlterField(
            model_name='widgetdata',
            name='widget',
            field=models.OneToOneField(to='widget_def.WidgetDefinition'),
        ),
    ]
