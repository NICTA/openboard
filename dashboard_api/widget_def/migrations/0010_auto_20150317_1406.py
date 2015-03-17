# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0009_auto_20150304_1118'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='widgetdeclaration',
            options={'ordering': ('theme', 'location', 'frequency', 'definition')},
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='theme',
            field=models.ForeignKey(blank=True, to='widget_def.Theme', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='widgetdeclaration',
            name='themes',
            field=models.ManyToManyField(related_name='oldthemes', to='widget_def.Theme'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdeclaration',
            unique_together=set([('theme', 'location', 'frequency', 'definition')]),
        ),
    ]
