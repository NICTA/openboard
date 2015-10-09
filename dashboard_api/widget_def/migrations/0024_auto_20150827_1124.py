# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0023_rawdatasetcolumn_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoDataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField(unique=True)),
                ('tiles', models.ManyToManyField(to='widget_def.TileDefinition')),
            ],
        ),
        migrations.CreateModel(
            name='GeoDatasetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dataset', models.ForeignKey(to='widget_def.GeoDataset')),
                ('frequency', models.ForeignKey(to='widget_def.Frequency')),
                ('location', models.ForeignKey(to='widget_def.Location')),
                ('theme', models.ForeignKey(to='widget_def.Theme')),
            ],
        ),
        migrations.CreateModel(
            name='GeoPropertyDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField()),
                ('label', models.CharField(max_length=256)),
                ('property_type', models.SmallIntegerField(choices=[(1, b'string'), (2, b'numeric'), (3, b'date'), (4, b'time'), (5, b'datetime')])),
                ('num_precision', models.SmallIntegerField(null=True, blank=True)),
                ('dataset', models.ForeignKey(to='widget_def.GeoDataset')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='geopropertydefinition',
            unique_together=set([('dataset', 'url'), ('dataset', 'label')]),
        ),
        migrations.AlterUniqueTogether(
            name='geodatasetdeclaration',
            unique_together=set([('dataset', 'theme', 'location', 'frequency')]),
        ),
    ]
