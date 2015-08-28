# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0025_geodataset_geom_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoWindow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'For internal reference only', unique=True, max_length=128)),
                ('north_east', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('south_west', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='geo_window',
            field=models.ForeignKey(blank=True, to='widget_def.GeoWindow', null=True),
        ),
    ]
