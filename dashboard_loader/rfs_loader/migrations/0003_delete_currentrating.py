# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rfs_loader', '0002_auto_20150330_1620'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CurrentRating',
        ),
    ]
