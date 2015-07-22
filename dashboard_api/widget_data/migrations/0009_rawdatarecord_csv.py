# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0008_auto_20150721_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawdatarecord',
            name='csv',
            field=models.TextField(null=True),
        ),
    ]
