# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0049_auto_20160329_1520'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('family', 'label')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='actual_frequency',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='actual_location',
        ),
    ]
