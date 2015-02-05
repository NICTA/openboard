# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0006_auto_20150204_0404'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tiledefinition',
            unique_together=set([('widget', 'url'), ('widget', 'sort_order')]),
        ),
    ]
