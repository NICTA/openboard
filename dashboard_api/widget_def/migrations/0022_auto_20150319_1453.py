# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0021_auto_20150319_1410'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('subcategory', 'sort_order'), ('url', 'actual_location', 'actual_frequency')]),
        ),
    ]
