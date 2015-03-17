# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0012_remove_widgetdeclaration_themes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widgetdeclaration',
            name='theme',
            field=models.ForeignKey(default=2, to='widget_def.Theme'),
            preserve_default=False,
        ),
    ]
