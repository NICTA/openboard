# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0038_auto_20150922_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficLightAutomation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField(unique=True)),
                ('target_value', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='trafficlightautostrategy',
            options={'ordering': ('url',)},
        ),
        migrations.RemoveField(
            model_name='trafficlightautostrategy',
            name='label',
        ),
        migrations.AddField(
            model_name='trafficlightautomation',
            name='strategy',
            field=models.ForeignKey(to='widget_def.TrafficLightAutoStrategy'),
        ),
        migrations.AddField(
            model_name='trafficlightautomation',
            name='target_statistic',
            field=models.ForeignKey(blank=True, to='widget_def.Statistic', null=True),
        ),
        migrations.AddField(
            model_name='statistic',
            name='traffic_light_automation',
            field=models.ForeignKey(blank=True, to='widget_def.TrafficLightAutomation', null=True),
        ),
    ]
