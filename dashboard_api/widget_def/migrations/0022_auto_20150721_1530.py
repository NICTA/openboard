# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0021_statistic_unit_si_prefix_rounding'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawDataSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('filename', models.CharField(max_length=128)),
                ('widget', models.ForeignKey(to='widget_def.WidgetDefinition')),
            ],
        ),
        migrations.CreateModel(
            name='RawDataSetColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField()),
                ('heading', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('rds', models.ForeignKey(to='widget_def.RawDataSet')),
            ],
            options={
                'ordering': ('rds', 'sort_order'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='rawdatasetcolumn',
            unique_together=set([('rds', 'sort_order')]),
        ),
        migrations.AlterUniqueTogether(
            name='rawdataset',
            unique_together=set([('widget', 'url')]),
        ),
    ]
