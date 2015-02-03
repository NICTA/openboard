# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ('sort_order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TileDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tile_type', models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph')])),
                ('expansion', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField()),
                ('am_pm', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['widget', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WidgetDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('url', models.SlugField()),
                ('expansion_hint', models.CharField(max_length=80)),
                ('source_url', models.URLField(max_length=400)),
                ('actual_frequency', models.CharField(max_length=40)),
                ('refresh_rate', models.IntegerField()),
                ('sort_order', models.IntegerField()),
                ('category', models.ForeignKey(to='widget_def.Category')),
                ('frequency', models.ForeignKey(to='widget_def.Frequency')),
                ('location', models.ForeignKey(to='widget_def.Location')),
                ('themes', models.ManyToManyField(to='widget_def.Theme')),
            ],
            options={
                'ordering': ('location', 'frequency', 'category', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('location', 'frequency', 'name'), ('location', 'frequency', 'category', 'sort_order'), ('location', 'frequency', 'url')]),
        ),
        migrations.AddField(
            model_name='tiledefinition',
            name='widget',
            field=models.ForeignKey(to='widget_def.WidgetDefinition'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tiledefinition',
            unique_together=set([('widget', 'sort_order')]),
        ),
        migrations.AlterModelOptions(
            name='frequency',
            options={'ordering': ('sort_order',), 'verbose_name_plural': 'frequencies'},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ('sort_order',)},
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ('sort_order',)},
        ),
        migrations.AddField(
            model_name='frequency',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='theme',
            name='sort_order',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
