# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport_static_loader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stoptime',
            name='shape_dist_travelled',
            field=models.DecimalField(null=True, max_digits=16, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
