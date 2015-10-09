# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0019_auto_20150708_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='requires_authentication',
            field=models.BooleanField(default=True),
        ),
    ]
