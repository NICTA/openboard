# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0051_viewtype_show_siblings'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawdataset',
            name='name',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
