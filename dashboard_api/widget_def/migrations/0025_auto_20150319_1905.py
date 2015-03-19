# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0024_auto_20150319_1850'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('family__subcategory', 'sort_order')},
        ),
        migrations.AlterField(
            model_name='widgetdefinition',
            name='family',
            field=models.ForeignKey(default=1, to='widget_def.WidgetFamily'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('family', 'actual_location', 'actual_frequency')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='url',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='subcategory',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='source_url',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='name',
        ),
    ]
