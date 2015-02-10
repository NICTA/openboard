# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0011_auto_20150211_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='name_as_label',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statistic',
            name='url',
            field=models.SlugField(default='foo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='statistic',
            name='name',
            field=models.CharField(max_length=80, blank=True),
            preserve_default=True,
        ),
    ]
