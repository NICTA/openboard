# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0015_graphdisplayoptions_rotates'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_aspect',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
