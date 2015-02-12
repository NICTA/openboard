# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
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
            name='Frequency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('url', models.SlugField(unique=True)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ('sort_order',),
                'verbose_name_plural': 'frequencies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IconCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.SlugField()),
                ('description', models.CharField(max_length=80)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ['scale', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IconLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('url', models.SlugField(unique=True)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ('sort_order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, blank=True)),
                ('url', models.SlugField()),
                ('name_as_label', models.BooleanField(default=True)),
                ('stat_type', models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm')])),
                ('trend', models.BooleanField(default=False)),
                ('num_precision', models.SmallIntegerField(null=True, blank=True)),
                ('unit_prefix', models.CharField(max_length=b'10', null=True, blank=True)),
                ('unit_suffix', models.CharField(max_length=b'10', null=True, blank=True)),
                ('unit_underfix', models.CharField(max_length=b'40', null=True, blank=True)),
                ('unit_signed', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField()),
                ('icon_library', models.ForeignKey(blank=True, to='widget_def.IconLibrary', null=True)),
            ],
            options={
                'ordering': ['tile', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('sort_order', models.IntegerField()),
                ('category', models.ForeignKey(to='widget_def.Category')),
            ],
            options={
                'ordering': ('category', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('url', models.SlugField(unique=True)),
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
                ('expansion', models.BooleanField(default=False, help_text=b'A widget must have one and only one non-expansion tile')),
                ('url', models.SlugField()),
                ('sort_order', models.IntegerField(help_text=b'Note: The default (non-expansion) tile is always sorted first')),
            ],
            options={
                'ordering': ['widget', 'expansion', 'sort_order'],
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
                ('sort_order', models.IntegerField(help_text=b'"Good" codes should have lower sort order than "Bad" codes.')),
                ('scale', models.ForeignKey(to='widget_def.TrafficLightScale')),
            ],
            options={
                'ordering': ['scale', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WidgetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ('location', 'frequency', 'definition'),
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
                ('actual_frequency_url', models.SlugField()),
                ('refresh_rate', models.IntegerField(help_text=b'in seconds')),
                ('sort_order', models.IntegerField()),
                ('subcategory', models.ForeignKey(to='widget_def.Subcategory')),
            ],
            options={
                'ordering': ('subcategory', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('url', 'actual_frequency_url'), ('name', 'actual_frequency_url'), ('subcategory', 'sort_order')]),
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='definition',
            field=models.ForeignKey(to='widget_def.WidgetDefinition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='frequency',
            field=models.ForeignKey(to='widget_def.Frequency'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='location',
            field=models.ForeignKey(to='widget_def.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='themes',
            field=models.ManyToManyField(to='widget_def.Theme'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdeclaration',
            unique_together=set([('location', 'frequency', 'definition')]),
        ),
        migrations.AlterUniqueTogether(
            name='trafficlightscalecode',
            unique_together=set([('scale', 'sort_order'), ('scale', 'value')]),
        ),
        migrations.AddField(
            model_name='tiledefinition',
            name='widget',
            field=models.ForeignKey(to='widget_def.WidgetDefinition'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tiledefinition',
            unique_together=set([('widget', 'url'), ('widget', 'sort_order')]),
        ),
        migrations.AlterUniqueTogether(
            name='subcategory',
            unique_together=set([('category', 'sort_order'), ('category', 'name')]),
        ),
        migrations.AddField(
            model_name='statistic',
            name='tile',
            field=models.ForeignKey(to='widget_def.TileDefinition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statistic',
            name='traffic_light_scale',
            field=models.ForeignKey(blank=True, to='widget_def.TrafficLightScale', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('tile', 'url'), ('tile', 'name')]),
        ),
        migrations.AddField(
            model_name='iconcode',
            name='scale',
            field=models.ForeignKey(to='widget_def.IconLibrary'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='iconcode',
            unique_together=set([('scale', 'sort_order'), ('scale', 'value')]),
        ),
    ]
