# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0022_auto_20150721_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawdatasetcolumn',
            name='url',
            field=models.SlugField(default='xxx'),
            preserve_default=False,
        ),
    ]
