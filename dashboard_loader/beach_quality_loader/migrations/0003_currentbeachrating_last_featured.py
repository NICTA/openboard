# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('beach_quality_loader', '0002_auto_20150311_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentbeachrating',
            name='last_featured',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 30, 22, 20, 25, 12915, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
