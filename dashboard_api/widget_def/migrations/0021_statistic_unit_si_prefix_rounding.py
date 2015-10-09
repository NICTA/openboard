# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0020_theme_requires_authentication'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='unit_si_prefix_rounding',
            field=models.IntegerField(default=0),
        ),
    ]
