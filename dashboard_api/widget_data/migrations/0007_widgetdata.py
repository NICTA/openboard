# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0041_statistic_editable'),
        ('widget_data', '0006_graphdata_last_updated'),
    ]

    operations = [
        migrations.CreateModel(
            name='WidgetData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('real_frequency_text', models.CharField(max_length=60, null=True, blank=True)),
                ('widget', models.ForeignKey(to='widget_def.WidgetDefinition', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
