# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0033_auto_20150324_0936'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistic',
            name='list_label_width',
        ),
    ]
