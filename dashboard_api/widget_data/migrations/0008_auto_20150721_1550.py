# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0022_auto_20150721_1530'),
        ('widget_data', '0007_auto_20150709_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1024, blank=True)),
                ('column', models.ForeignKey(to='widget_def.RawDataSetColumn')),
            ],
            options={
                'ordering': ('record', 'column'),
            },
        ),
        migrations.CreateModel(
            name='RawDataRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField()),
                ('rds', models.ForeignKey(to='widget_def.RawDataSet')),
            ],
            options={
                'ordering': ('rds', 'sort_order'),
            },
        ),
        migrations.AddField(
            model_name='rawdata',
            name='record',
            field=models.ForeignKey(to='widget_data.RawDataRecord'),
        ),
        migrations.AlterUniqueTogether(
            name='rawdatarecord',
            unique_together=set([('rds', 'sort_order')]),
        ),
        migrations.AlterUniqueTogether(
            name='rawdata',
            unique_together=set([('record', 'column')]),
        ),
    ]
