# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0045_auto_20160323_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geopropertydefinition',
            name='label',
            field=models.CharField(max_length=256, verbose_name=b'name'),
        ),
        migrations.AlterField(
            model_name='geopropertydefinition',
            name='url',
            field=models.SlugField(verbose_name=b'label'),
        ),
    ]
