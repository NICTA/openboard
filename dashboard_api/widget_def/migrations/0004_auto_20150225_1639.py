# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0003_remove_widgetdefinition_last_updated'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('url', 'actual_frequency_url'), ('subcategory', 'sort_order')]),
        ),
    ]
