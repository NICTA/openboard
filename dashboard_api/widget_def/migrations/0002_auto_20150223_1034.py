# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='widgetdefinition',
            name='about',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 22, 23, 34, 11, 972378, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
