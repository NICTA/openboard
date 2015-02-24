# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0002_auto_20150223_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='last_updated',
        ),
    ]
