# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_loader', '0005_auto_20150323_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loader',
            name='locked_by_thread',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=0, blank=True),
            preserve_default=True,
        ),
    ]
