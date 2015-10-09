# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0028_auto_20150828_1120'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geopropertydefinition',
            options={'ordering': ('dataset', 'sort_order')},
        ),
        migrations.AddField(
            model_name='geopropertydefinition',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='geopropertydefinition',
            unique_together=set([('dataset', 'sort_order'), ('dataset', 'url'), ('dataset', 'label')]),
        ),
    ]
