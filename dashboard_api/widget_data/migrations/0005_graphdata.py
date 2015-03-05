# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0009_auto_20150304_1118'),
        ('widget_data', '0004_auto_20150227_1454'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('horiz_numericval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('horiz_dateval', models.DateField(null=True, blank=True)),
                ('horiz_timeval', models.TimeField(null=True, blank=True)),
                ('cluster', models.ForeignKey(blank=True, to='widget_def.GraphCluster', null=True)),
                ('dataset', models.ForeignKey(blank=True, to='widget_def.GraphDataset', null=True)),
                ('graph', models.ForeignKey(to='widget_def.GraphDefinition')),
            ],
            options={
                'ordering': ('graph', 'cluster', 'dataset'),
            },
            bases=(models.Model,),
        ),
    ]
