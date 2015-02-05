# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0004_auto_20150204_0249'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_frequency_url',
            field=models.SlugField(default='xxx'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('url', 'actual_frequency_url'), ('category', 'sort_order'), ('name', 'actual_frequency_url')]),
        ),
    ]
