# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0032_auto_20150902_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='geopropertydefinition',
            name='data_property',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='geodataset',
            unique_together=set([('subcategory', 'label'), ('subcategory', 'sort_order')]),
        ),
    ]
