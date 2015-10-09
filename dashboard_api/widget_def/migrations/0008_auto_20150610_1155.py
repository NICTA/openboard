# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0007_auto_20150610_1114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='graphcluster',
            options={'ordering': ['graph', 'sort_order']},
        ),
        migrations.AlterModelOptions(
            name='graphdataset',
            options={'ordering': ['graph', 'sort_order']},
        ),
        migrations.AddField(
            model_name='graphcluster',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='graphdisplayoptions',
            name='shaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='graphcluster',
            unique_together=set([('graph', 'url'), ('graph', 'sort_order'), ('graph', 'label')]),
        ),
        migrations.AlterUniqueTogether(
            name='graphdataset',
            unique_together=set([('graph', 'url'), ('graph', 'sort_order'), ('graph', 'label')]),
        ),
    ]
