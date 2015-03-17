# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0011_auto_20150317_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='widgetdeclaration',
            name='themes',
        ),
    ]
