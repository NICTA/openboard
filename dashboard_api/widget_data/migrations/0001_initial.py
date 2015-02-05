# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0004_auto_20150204_0249'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=120, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('statistic', models.ForeignKey(to='widget_def.Statistic', unique=True)),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatisticListItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyval', models.CharField(max_length=120, null=True, blank=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=120, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('sort_order', models.IntegerField()),
                ('statistic', models.ForeignKey(to='widget_def.Statistic')),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
            ],
            options={
                'ordering': ('statistic', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitems',
            unique_together=set([('statistic', 'sort_order')]),
        ),
    ]
