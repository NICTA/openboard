# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0034_auto_20150904_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='geodataset',
            name='ext_extra',
            field=models.CharField(help_text=b'For External Datasets only - optional extra json for the Terria catalog.  Should be a valid json object if set', max_length=256, null=True, blank=True),
        ),
    ]
