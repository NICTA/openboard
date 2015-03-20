# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0026_auto_20150320_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widgetdefinition',
            name='sort_order',
            field=models.IntegerField(unique=True),
            preserve_default=True,
        ),
    ]
