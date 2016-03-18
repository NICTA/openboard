# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0040_auto_20160318_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='widgetview',
            options={'ordering': ['sort_order']},
        ),
        migrations.AddField(
            model_name='widgetview',
            name='view_type',
            field=models.ForeignKey(default=1, to='widget_def.ViewType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='widgetview',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='widget_def.WidgetView', null=True),
        ),
    ]
