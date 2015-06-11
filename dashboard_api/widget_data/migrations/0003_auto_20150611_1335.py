# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0002_auto_20150519_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphdata',
            name='horiz_numericval',
            field=models.DecimalField(null=True, max_digits=14, decimal_places=4, blank=True),
        ),
        migrations.AlterField(
            model_name='graphdata',
            name='value',
            field=models.DecimalField(null=True, max_digits=14, decimal_places=4, blank=True),
        ),
    ]
