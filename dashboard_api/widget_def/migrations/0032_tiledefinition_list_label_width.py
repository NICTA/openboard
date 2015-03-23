# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0031_auto_20150323_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='list_label_width',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(100)]),
            preserve_default=True,
        ),
    ]
