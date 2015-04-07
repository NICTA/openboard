# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beach_quality_loader', '0003_currentbeachrating_last_featured'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currentbeachrating',
            name='last_featured',
        ),
    ]
