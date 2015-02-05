# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0005_auto_20150204_0351'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiledefinition',
            name='url',
            field=models.SlugField(default='xxx'),
            preserve_default=False,
        ),
    ]
