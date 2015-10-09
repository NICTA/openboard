# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rfs_loader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentrating',
            name='rating_text',
            field=models.CharField(default='High', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='currentrating',
            name='tlc',
            field=models.CharField(default=2, max_length=50),
            preserve_default=False,
        ),
    ]
