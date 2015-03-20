# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0025_auto_20150319_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='GridColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ('grid', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GridDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('corner_label', models.CharField(max_length=50)),
                ('tile', models.ForeignKey(to='widget_def.TileDefinition', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GridRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
                ('sort_order', models.IntegerField()),
                ('grid', models.ForeignKey(to='widget_def.GridDefinition')),
            ],
            options={
                'ordering': ('grid', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GridStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('column', models.ForeignKey(to='widget_def.GridColumn')),
                ('grid', models.ForeignKey(to='widget_def.GridDefinition')),
                ('row', models.ForeignKey(to='widget_def.GridRow')),
                ('statistic', models.ForeignKey(to='widget_def.Statistic')),
            ],
            options={
                'ordering': ('grid', 'row', 'column'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gridstatistic',
            unique_together=set([('grid', 'statistic'), ('grid', 'column', 'row')]),
        ),
        migrations.AlterUniqueTogether(
            name='gridrow',
            unique_together=set([('grid', 'label'), ('grid', 'sort_order')]),
        ),
        migrations.AddField(
            model_name='gridcolumn',
            name='grid',
            field=models.ForeignKey(to='widget_def.GridDefinition'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gridcolumn',
            unique_together=set([('grid', 'label'), ('grid', 'sort_order')]),
        ),
        migrations.AddField(
            model_name='widgetfamily',
            name='subtitle',
            field=models.CharField(max_length=60, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid')]),
            preserve_default=True,
        ),
    ]
