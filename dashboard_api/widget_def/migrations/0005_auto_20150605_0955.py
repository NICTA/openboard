# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0004_auto_20150529_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='columns',
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='list_label_width',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
