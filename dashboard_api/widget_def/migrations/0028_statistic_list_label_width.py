# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0027_auto_20150320_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='list_label_width',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(80)]),
            preserve_default=True,
        ),
    ]
