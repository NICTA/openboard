# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'widget_def', '0001_initial'), (b'widget_def', '0002_auto_20150203_0002'), (b'widget_def', '0003_auto_20150203_0253'), (b'widget_def', '0004_auto_20150204_0249'), (b'widget_def', '0005_auto_20150204_0351'), (b'widget_def', '0006_auto_20150204_0404'), (b'widget_def', '0007_auto_20150204_0406'), (b'widget_def', '0008_auto_20150205_2334'), (b'widget_def', '0009_auto_20150210_1442'), (b'widget_def', '0010_auto_20150211_0901'), (b'widget_def', '0011_auto_20150211_0908'), (b'widget_def', '0012_auto_20150211_0936'), (b'widget_def', '0013_auto_20150211_0940')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Frequency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('url', models.SlugField(unique=True)),
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('url', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
                ('themes', models.ManyToManyField(to=b'widget_def.Theme')),
            ],
            options={
                'ordering': ('location', 'frequency', 'category', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('location', 'frequency', 'category', 'sort_order'), ('location', 'frequency', 'name'), ('location', 'frequency', 'url')]),
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
        migrations.CreateModel(
            name='WidgetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('definition', models.ForeignKey(to='widget_def.WidgetDefinition')),
                ('frequency', models.ForeignKey(to='widget_def.Frequency')),
                ('location', models.ForeignKey(to='widget_def.Location')),
                ('themes', models.ManyToManyField(to=b'widget_def.Theme')),
            ],
            options={
                'ordering': ('location', 'frequency', 'definition'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdeclaration',
            unique_together=set([('location', 'frequency', 'definition')]),
        ),
        migrations.AlterModelOptions(
            name='tiledefinition',
            options={'ordering': ['widget', 'expansion', 'sort_order']},
        ),
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('category', 'sort_order')},
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='am_pm',
            field=models.BooleanField(default=False, help_text=b'Only used for single_main_stat type tiles'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='expansion',
            field=models.BooleanField(default=False, help_text=b'A widget must have one and only one non-expansion tile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='sort_order',
            field=models.IntegerField(help_text=b'Note: The default (non-expansion) tile is always sorted first'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trafficlightscalecode',
            name='sort_order',
            field=models.IntegerField(help_text=b'"Good" codes should have lower sort order than "Bad" codes.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='widgetdefinition',
            name='refresh_rate',
            field=models.IntegerField(help_text=b'in seconds'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('category', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='themes',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='location',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='frequency',
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_frequency_url',
            field=models.SlugField(default='xxx'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('url', 'actual_frequency_url'), ('category', 'sort_order'), ('name', 'actual_frequency_url')]),
        ),
        migrations.AddField(
            model_name='tiledefinition',
            name='url',
            field=models.SlugField(default='xxx'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='tiledefinition',
            unique_together=set([('widget', 'url'), ('widget', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='tiledefinition',
            name='am_pm',
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm')]),
            preserve_default=True,
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
        migrations.AddField(
            model_name='statistic',
            name='icon_library',
            field=models.ForeignKey(blank=True, to='widget_def.IconLibrary', null=True),
            preserve_default=True,
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
        migrations.AlterUniqueTogether(
            name='subcategory',
            unique_together=set([('category', 'sort_order'), ('category', 'name')]),
        ),
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('subcategory', 'sort_order')},
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='subcategory',
            field=models.ForeignKey(default=1, to='widget_def.Subcategory'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('url', 'actual_frequency_url'), ('name', 'actual_frequency_url'), ('subcategory', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='category',
        ),
        migrations.AddField(
            model_name='statistic',
            name='name_as_label',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statistic',
            name='url',
            field=models.SlugField(default='foo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='statistic',
            name='name',
            field=models.CharField(max_length=80, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('tile', 'url'), ('tile', 'name')]),
        ),
    ]
