# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0053_auto_20160503_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawdataset',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='rawdataset',
            unique_together=set([('widget', 'url'), ('widget', 'name')]),
        ),
    ]
