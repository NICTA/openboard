# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0025_geodataset_geom_type'),
        ('widget_data', '0009_rawdatarecord_csv'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
                ('dataset', models.ForeignKey(to='widget_def.GeoDataset')),
            ],
        ),
        migrations.CreateModel(
            name='GeoProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('decval', models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)),
                ('strval', models.CharField(max_length=400, null=True, blank=True)),
                ('dateval', models.DateField(null=True, blank=True)),
                ('timeval', models.TimeField(null=True, blank=True)),
                ('datetimeval', models.DateTimeField(null=True, blank=True)),
                ('feature', models.ForeignKey(to='widget_data.GeoFeature')),
                ('prop', models.ForeignKey(to='widget_def.GeoPropertyDefinition')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='geoproperty',
            unique_together=set([('feature', 'prop')]),
        ),
    ]
