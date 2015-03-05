# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0005_graphdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdata',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 4, 2, 19, 720164, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
