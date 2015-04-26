# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0043_auto_20150417_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphdefinition',
            name='tile',
            field=models.OneToOneField(to='widget_def.TileDefinition'),
        ),
        migrations.AlterField(
            model_name='griddefinition',
            name='tile',
            field=models.OneToOneField(to='widget_def.TileDefinition'),
        ),
    ]
