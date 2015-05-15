# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators

class Migration(migrations.Migration):

    replaces = [
    ]

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
        ),
        migrations.CreateModel(
            name='IconLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
            ],
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
        ),
        migrations.CreateModel(
            name='TrafficLightScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
            ],
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
        ),
        migrations.CreateModel(
            name='WidgetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ('location', 'frequency', 'definition'),
            },
        ),
        migrations.CreateModel(
            name='WidgetDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expansion_hint', models.CharField(max_length=80)),
                ('actual_frequency', models.CharField(max_length=40)),
                ('refresh_rate', models.IntegerField(help_text=b'in seconds')),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ('sort_order'),
            },
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='definition',
            field=models.ForeignKey(to='widget_def.WidgetDefinition'),
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='frequency',
            field=models.ForeignKey(to='widget_def.Frequency'),
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='location',
            field=models.ForeignKey(to='widget_def.Location'),
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
        ),
        migrations.AddField(
            model_name='statistic',
            name='traffic_light_scale',
            field=models.ForeignKey(blank=True, to='widget_def.TrafficLightScale', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together=set([('tile', 'url'), ('tile', 'name')]),
        ),
        migrations.AddField(
            model_name='iconcode',
            name='scale',
            field=models.ForeignKey(to='widget_def.IconLibrary'),
        ),
        migrations.AlterUniqueTogether(
            name='iconcode',
            unique_together=set([('scale', 'sort_order'), ('scale', 'value')]),
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='about',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='statistic',
            name='hyperlinkable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm'), (7, b'event_list')]),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar')]),
        ),
        migrations.CreateModel(
            name='GraphCluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('label', models.CharField(max_length=80)),
            ],
            options={
                'ordering': ['graph', 'url'],
            },
        ),
        migrations.CreateModel(
            name='GraphDataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('label', models.CharField(max_length=80)),
                ('colour', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['graph', 'url'],
            },
        ),
        migrations.CreateModel(
            name='GraphDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('heading', models.CharField(max_length=120, null=True, blank=True)),
                ('graph_type', models.SmallIntegerField(choices=[(1, b'line'), (2, b'histogram'), (3, b'bar'), (4, b'pie')])),
                ('numeric_axis_label', models.CharField(max_length=120, null=True, blank=True)),
                ('numeric_axis_always_show_zero', models.BooleanField(default=True)),
                ('horiz_axis_label', models.CharField(max_length=120, null=True, blank=True)),
                ('horiz_axis_type', models.SmallIntegerField(default=0, choices=[(0, b'-'), (1, b'numeric'), (2, b'date'), (3, b'time')])),
                ('tile', models.ForeignKey(to='widget_def.TileDefinition', unique=True)),
                ('secondary_numeric_axis_always_show_zero', models.BooleanField(default=True)),
                ('secondary_numeric_axis_label', models.CharField(max_length=120, null=True, blank=True)),
                ('use_secondary_numeric_axis', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('tile',),
            },
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='graph',
            field=models.ForeignKey(to='widget_def.GraphDefinition'),
        ),
        migrations.AlterUniqueTogether(
            name='graphdataset',
            unique_together=set([('graph', 'url'), ('graph', 'label')]),
        ),
        migrations.AddField(
            model_name='graphcluster',
            name='graph',
            field=models.ForeignKey(to='widget_def.GraphDefinition'),
        ),
        migrations.AlterUniqueTogether(
            name='graphcluster',
            unique_together=set([('graph', 'url'), ('graph', 'label')]),
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='use_secondary_numeric_axis',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='widgetdeclaration',
            options={'ordering': ('theme', 'location', 'frequency', 'definition')},
        ),
        migrations.AddField(
            model_name='widgetdeclaration',
            name='theme',
            field=models.ForeignKey(blank=True, to='widget_def.Theme', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdeclaration',
            unique_together=set([('theme', 'location', 'frequency', 'definition')]),
        ),
        migrations.AlterField(
            model_name='widgetdeclaration',
            name='theme',
            field=models.ForeignKey(default=2, to='widget_def.Theme'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='frequency',
            name='display_mode',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='frequency',
            name='actual_display',
            field=models.CharField(default='Real time', unique=True, max_length=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_location',
            field=models.ForeignKey(default=3, to='widget_def.Location'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='actual_frequency',
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='actual_frequency',
            field=models.ForeignKey(default=2, to='widget_def.Frequency'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='WidgetFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('url', models.SlugField(unique=True)),
                ('source_url', models.URLField(max_length=400)),
                ('subcategory', models.ForeignKey(to='widget_def.Subcategory')),
            ],
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='family',
            field=models.ForeignKey(blank=True, to='widget_def.WidgetFamily', null=True),
        ),
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('family__subcategory', 'sort_order')},
        ),
        migrations.AlterField(
            model_name='widgetdefinition',
            name='family',
            field=models.ForeignKey(default=1, to='widget_def.WidgetFamily'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('family', 'actual_location', 'actual_frequency')]),
        ),
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
        ),
        migrations.CreateModel(
            name='GridDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('corner_label', models.CharField(max_length=50)),
                ('tile', models.ForeignKey(to='widget_def.TileDefinition', unique=True)),
            ],
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
        ),
        migrations.AlterUniqueTogether(
            name='gridcolumn',
            unique_together=set([('grid', 'label'), ('grid', 'sort_order')]),
        ),
        migrations.AddField(
            model_name='widgetfamily',
            name='subtitle',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid')]),
        ),
        migrations.AlterField(
            model_name='widgetdefinition',
            name='sort_order',
            field=models.IntegerField(unique=True),
        ),
        migrations.AddField(
            model_name='statistic',
            name='list_label_width',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(80)]),
        ),
        migrations.AddField(
            model_name='griddefinition',
            name='show_column_headers',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='griddefinition',
            name='show_row_headers',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='griddefinition',
            name='corner_label',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid'), (10, b'single_list_stat')]),
        ),
        migrations.AddField(
            model_name='tiledefinition',
            name='list_label_width',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.RemoveField(
            model_name='statistic',
            name='list_label_width',
        ),
        migrations.AddField(
            model_name='widgetfamily',
            name='source_url_text',
            field=models.CharField(default='Agency Website', max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (10, b'single_list_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid'), (11, b'newsfeed')]),
        ),
        migrations.AddField(
            model_name='statistic',
            name='footer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (8, b'long_string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (6, b'am_pm'), (7, b'event_list')]),
        ),
        migrations.AddField(
            model_name='statistic',
            name='rotates',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='statistic',
            name='editable',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='tile_type',
            field=models.SmallIntegerField(choices=[(1, b'single_main_stat'), (2, b'double_main_stat'), (10, b'single_list_stat'), (3, b'priority_list'), (4, b'urgency_list'), (5, b'list_overflow'), (6, b'graph'), (8, b'calendar'), (9, b'grid'), (11, b'newsfeed'), (12, b'news_ticker')]),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='stat_type',
            field=models.SmallIntegerField(choices=[(1, b'string'), (8, b'long_string'), (2, b'numeric'), (3, b'string_kv_list'), (4, b'numeric_kv_list'), (5, b'string_list'), (9, b'long_string_list'), (6, b'am_pm'), (7, b'event_list')]),
        ),
        migrations.AlterField(
            model_name='graphdefinition',
            name='tile',
            field=models.OneToOneField(to='widget_def.TileDefinition'),
        ),
        migrations.AlterField(
            model_name='griddefinition',
            name='tile',
            field=models.OneToOneField(to='widget_def.TileDefinition'),
        ),
    ]
