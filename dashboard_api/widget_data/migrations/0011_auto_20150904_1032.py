# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0010_auto_20150827_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='geofeature',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 4, 0, 32, 11, 286507, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='geoproperty',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 4, 0, 32, 19, 910687, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
