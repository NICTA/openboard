# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-27 00:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0077_auto_20161027_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewfamilymember',
            name='sort_order',
            field=models.IntegerField(help_text=b'How the views are sorted within the family'),
        ),
    ]
