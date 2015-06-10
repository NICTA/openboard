# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0005_auto_20150605_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphDisplayOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lines', models.SmallIntegerField(default=0, choices=[(0, b'none'), (1, b'straight lines'), (2, b'smooth curves')])),
                ('points', models.SmallIntegerField(default=0, choices=[(0, b'none'), (1, b'circle'), (2, b'square'), (3, b'triangle'), (4, b'vertical-bars')])),
                ('single_graph', models.BooleanField(default=True)),
                ('stacked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PointColourMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(unique=True, max_length=50)),
                ('decimal_places', models.SmallIntegerField(default=0)),
            ],
            options={
                'ordering': ('label',),
            },
        ),
        migrations.CreateModel(
            name='PointColourRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_value_dec', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('min_value_int', models.IntegerField(null=True, blank=True)),
                ('colour', models.CharField(max_length=50)),
                ('colour_map', models.ForeignKey(to='widget_def.PointColourMap')),
            ],
            options={
                'ordering': ('colour_map', 'min_value_dec', 'min_value_int'),
            },
        ),
        migrations.RemoveField(
            model_name='graphdefinition',
            name='stacked',
        ),
        migrations.AddField(
            model_name='graphdisplayoptions',
            name='graph',
            field=models.OneToOneField(to='widget_def.GraphDefinition'),
        ),
        migrations.AddField(
            model_name='graphdisplayoptions',
            name='point_colour_map',
            field=models.ForeignKey(blank=True, to='widget_def.PointColourMap', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='pointcolourrange',
            unique_together=set([('colour_map', 'min_value_dec', 'min_value_int')]),
        ),
    ]
