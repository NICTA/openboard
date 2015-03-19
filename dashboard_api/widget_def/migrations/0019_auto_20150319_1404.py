# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0018_auto_20150319_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_frequency',
            field=models.ForeignKey(default=2, to='widget_def.Frequency'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('url', 'actual_frequency_url'), ('subcategory', 'sort_order')]),
        ),
    ]
