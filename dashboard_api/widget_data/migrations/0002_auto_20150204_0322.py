# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticdata',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 4, 3, 22, 13, 334267, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statisticlistitems',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 4, 3, 22, 21, 513904, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
