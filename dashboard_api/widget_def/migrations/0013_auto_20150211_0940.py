# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0012_auto_20150211_0936'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('tile', 'url'), ('tile', 'name')]),
        ),
    ]
