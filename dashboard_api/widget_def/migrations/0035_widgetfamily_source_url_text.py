# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0034_remove_statistic_list_label_width'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetfamily',
            name='source_url_text',
            field=models.CharField(default='Agency Website', max_length=60),
            preserve_default=False,
        ),
    ]
