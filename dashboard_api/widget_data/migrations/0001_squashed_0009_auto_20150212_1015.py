# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    replaces = [(b'widget_data', '0001_initial'), (b'widget_data', '0002_auto_20150204_0322'), (b'widget_data', '0003_auto_20150204_0618'), (b'widget_data', '0004_auto_20150206_0315'), (b'widget_data', '0005_auto_20150210_1442'), (b'widget_data', '0006_statisticdata_label'), (b'widget_data', '0007_auto_20150211_1430'), (b'widget_data', '0008_auto_20150212_1010'), (b'widget_data', '0009_auto_20150212_1015')]

    dependencies = [
        ('widget_def', '0001_squashed_0013_auto_20150211_0940'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=400, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('statistic', models.ForeignKey(to='widget_def.Statistic', unique=True)),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
                ('last_updated', models.DateTimeField(default=datetime.datetime(2015, 2, 4, 3, 22, 13, 334267, tzinfo=utc), auto_now=True)),
                ('icon_code', models.ForeignKey(blank=True, to='widget_def.IconCode', null=True)),
                ('label', models.CharField(max_length=80, null=True, blank=True)),
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
        migrations.AddField(
            model_name='statisticlistitems',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 4, 3, 22, 21, 513904, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='StatisticListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyval', models.CharField(max_length=120, null=True, blank=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=120, null=True, blank=True)),
                ('trend', models.SmallIntegerField(blank=True, null=True, choices=[(1, b'Upwards'), (0, b'Steady'), (-1, b'Downwards')])),
                ('sort_order', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('statistic', models.ForeignKey(to='widget_def.Statistic', unique=True)),
                ('traffic_light_code', models.ForeignKey(blank=True, to='widget_def.TrafficLightScaleCode', null=True)),
            ],
            options={
                'ordering': ('statistic', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitems',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='statisticlistitems',
            name='statistic',
        ),
        migrations.RemoveField(
            model_name='statisticlistitems',
            name='traffic_light_code',
        ),
        migrations.DeleteModel(
            name='StatisticListItems',
        ),
        migrations.AlterUniqueTogether(
            name='statisticlistitem',
            unique_together=set([('statistic', 'sort_order')]),
        ),
        migrations.AlterField(
            model_name='statisticlistitem',
            name='statistic',
            field=models.ForeignKey(to='widget_def.Statistic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statisticlistitem',
            name='icon_code',
            field=models.ForeignKey(blank=True, to='widget_def.IconCode', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='statisticlistitem',
            name='strval',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='statisticlistitem',
            name='strval',
            field=models.CharField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='statisticlistitem',
            name='strval',
            field=models.CharField(max_length=400, null=True, blank=True),
            preserve_default=True,
        ),
    ]
