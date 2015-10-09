# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0027_auto_20150828_1051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geodataset',
            options={'ordering': ('subcategory', 'sort_order')},
        ),
        migrations.AlterModelOptions(
            name='geodatasetdeclaration',
            options={'ordering': ('dataset', 'theme', 'location', 'frequency')},
        ),
        migrations.AddField(
            model_name='geodataset',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='geodataset',
            name='subcategory',
            field=models.ForeignKey(default=1, to='widget_def.Subcategory'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='geodataset',
            unique_together=set([('subcategory', 'sort_order')]),
        ),
    ]
