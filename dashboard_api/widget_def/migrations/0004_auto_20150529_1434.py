# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0003_auto_20150528_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphcluster',
            name='hyperlink',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='hyperlink',
            field=models.URLField(null=True, blank=True),
        ),
    ]
