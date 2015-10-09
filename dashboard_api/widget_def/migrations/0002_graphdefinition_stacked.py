# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdefinition',
            name='stacked',
            field=models.BooleanField(default=False),
        ),
    ]
