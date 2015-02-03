# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0002_auto_20150203_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(blank=True)),
                ('stat_type', models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list')])),
                ('trend', models.BooleanField(default=False)),
                ('num_precision', models.SmallIntegerField(null=True, blank=True)),
                ('unit_prefix', models.CharField(max_length=b'10', null=True, blank=True)),
                ('unit_suffix', models.CharField(max_length=b'10', null=True, blank=True)),
                ('unit_underfix', models.CharField(max_length=b'40', null=True, blank=True)),
                ('unit_signed', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField()),
                ('tile', models.ForeignKey(to='widget_def.TileDefinition')),
            ],
            options={
                'ordering': ['tile', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrafficLightScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrafficLightScaleCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.SlugField()),
                ('colour', models.CharField(max_length=50)),
                ('sort_order', models.IntegerField()),
                ('scale', models.ForeignKey(to='widget_def.TrafficLightScale')),
            ],
            options={
                'ordering': ['scale', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='trafficlightscalecode',
            unique_together=set([('scale', 'sort_order'), ('scale', 'value')]),
        ),
        migrations.AddField(
            model_name='statistic',
            name='traffic_light_scale',
            field=models.ForeignKey(blank=True, to='widget_def.TrafficLightScale', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('tile', 'name')]),
        ),
    ]
