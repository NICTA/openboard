# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0007_auto_20150227_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphCluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('label', models.CharField(max_length=80)),
            ],
            options={
                'ordering': ['graph', 'url'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GraphDataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('label', models.CharField(max_length=80)),
                ('colour', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['graph', 'url'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GraphDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('heading', models.CharField(max_length=120, null=True, blank=True)),
                ('graph_type', models.SmallIntegerField(choices=[(1, b'line'), (2, b'histogram'), (3, b'bar'), (4, b'pie')])),
                ('numeric_axis_label', models.CharField(max_length=120, null=True, blank=True)),
                ('numeric_axis_always_show_zero', models.BooleanField(default=True)),
                ('horiz_axis_label', models.CharField(max_length=120, null=True, blank=True)),
                ('horiz_axis_type', models.SmallIntegerField(default=0, choices=[(0, b'-'), (1, b'numeric'), (2, b'date'), (3, b'time')])),
                ('tile', models.ForeignKey(to='widget_def.TileDefinition', unique=True)),
            ],
            options={
                'ordering': ('tile',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='graph',
            field=models.ForeignKey(to='widget_def.GraphDefinition'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='graphdataset',
            unique_together=set([('graph', 'url'), ('graph', 'label')]),
        ),
        migrations.AddField(
            model_name='graphcluster',
            name='graph',
            field=models.ForeignKey(to='widget_def.GraphDefinition'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='graphcluster',
            unique_together=set([('graph', 'url'), ('graph', 'label')]),
        ),
    ]
