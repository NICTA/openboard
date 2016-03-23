# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0044_auto_20160321_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewGeoDatasetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AlterField(
            model_name='geodataset',
            name='label',
            field=models.CharField(max_length=128, verbose_name=b'name'),
        ),
        migrations.AlterField(
            model_name='geodataset',
            name='url',
            field=models.SlugField(unique=True, verbose_name=b'label'),
        ),
        migrations.AlterField(
            model_name='graphcluster',
            name='label',
            field=models.CharField(max_length=80, verbose_name=b'name'),
        ),
        migrations.AlterField(
            model_name='graphcluster',
            name='url',
            field=models.SlugField(verbose_name=b'label'),
        ),
        migrations.AlterField(
            model_name='graphdataset',
            name='label',
            field=models.CharField(max_length=80, verbose_name=b'name'),
        ),
        migrations.AlterField(
            model_name='graphdataset',
            name='url',
            field=models.SlugField(verbose_name=b'label'),
        ),
        migrations.AlterField(
            model_name='gridcolumn',
            name='label',
            field=models.CharField(max_length=50, verbose_name=b'header'),
        ),
        migrations.AlterField(
            model_name='griddefinition',
            name='corner_label',
            field=models.CharField(max_length=50, null=True, verbose_name=b'corner header', blank=True),
        ),
        migrations.AlterField(
            model_name='gridrow',
            name='label',
            field=models.CharField(max_length=50, verbose_name=b'header'),
        ),
        migrations.AlterField(
            model_name='pointcolourmap',
            name='label',
            field=models.CharField(unique=True, max_length=50, verbose_name=b'name'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='name_as_label',
            field=models.BooleanField(default=True, verbose_name=b'display_name'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='url',
            field=models.SlugField(verbose_name=b'label'),
        ),
        migrations.AddField(
            model_name='viewgeodatasetdeclaration',
            name='dataset',
            field=models.ForeignKey(to='widget_def.GeoDataset'),
        ),
        migrations.AddField(
            model_name='viewgeodatasetdeclaration',
            name='view',
            field=models.ForeignKey(to='widget_def.WidgetView'),
        ),
    ]
