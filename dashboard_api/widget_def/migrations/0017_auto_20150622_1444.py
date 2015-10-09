# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0016_category_category_aspect'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='widgetfamily',
            options={'ordering': ('subcategory',)},
        ),
    ]
