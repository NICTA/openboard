# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0037_geodataset_colour_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficLightAutoRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_val', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('map_val', models.CharField(max_length=400, null=True, blank=True)),
                ('default_val', models.BooleanField(default=False)),
                ('code', models.ForeignKey(to='widget_def.TrafficLightScaleCode')),
            ],
            options={
                'ordering': ('strategy', 'default_val', 'min_val', 'map_val'),
            },
        ),
        migrations.CreateModel(
            name='TrafficLightAutoStrategy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(unique=True, max_length=128)),
                ('url', models.SlugField(unique=True)),
                ('strategy_type', models.SmallIntegerField(choices=[(1, b'relative'), (2, b'absolute'), (3, b'map')])),
                ('scale', models.ForeignKey(to='widget_def.TrafficLightScale')),
            ],
            options={
                'ordering': ('label',),
            },
        ),
        migrations.AddField(
            model_name='trafficlightautorule',
            name='strategy',
            field=models.ForeignKey(to='widget_def.TrafficLightAutoStrategy'),
        ),
        migrations.AlterUniqueTogether(
            name='trafficlightautorule',
            unique_together=set([('strategy', 'default_val', 'min_val', 'map_val')]),
        ),
    ]
