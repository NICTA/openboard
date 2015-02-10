# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0010_auto_20150211_0901'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('subcategory', 'sort_order')},
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='subcategory',
            field=models.ForeignKey(default=1, to='widget_def.Subcategory'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('url', 'actual_frequency_url'), ('subcategory', 'sort_order'), ('name', 'actual_frequency_url')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='category',
        ),
    ]
