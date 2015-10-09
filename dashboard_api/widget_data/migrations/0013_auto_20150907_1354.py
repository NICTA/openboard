# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0012_auto_20150907_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoproperty',
            name='decval',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=4, blank=True),
        ),
    ]
