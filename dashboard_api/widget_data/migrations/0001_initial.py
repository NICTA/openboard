# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):
    
    replaces = [
    ]

    dependencies = [
        ("widget_def", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=80, null=True, blank=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=400, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('icon_code', models.ForeignKey(blank=True, to='widget_def.IconCode', null=True)),
                ('statistic', models.OneToOneField(to='widget_def.Statistic')),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatisticListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyval', models.CharField(max_length=120, null=True, blank=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=400, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('sort_order', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('icon_code', models.ForeignKey(blank=True, to='widget_def.IconCode', null=True)),
                ('statistic', models.ForeignKey(to='widget_def.Statistic')),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
            ],
            options={
                'ordering': ('statistic', 'sort_order'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitem',
            unique_together=set([('statistic', 'sort_order')]),
        ),
        migrations.AddField(
            model_name='statisticlistitem',
            name='datekey',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='statisticlistitem',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitem',
            unique_together=set([('statistic', 'datekey', 'sort_order')]),
        ),
        migrations.AlterModelOptions(
            name='statisticlistitem',
            options={'ordering': ('statistic', 'datekey', 'sort_order')},
        ),
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
                ('last_updated', models.DateTimeField(default=datetime.datetime(2015, 3, 4, 4, 2, 19, 720164, tzinfo=utc), auto_now=True)),
            ],
            options={
                'ordering': ('graph', 'cluster', 'dataset'),
            },
        ),
        migrations.CreateModel(
            name='WidgetData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actual_frequency_text', models.CharField(max_length=60, null=True, blank=True)),
                ('widget', models.OneToOneField(to='widget_def.WidgetDefinition')),
            ],
        ),
    ]
