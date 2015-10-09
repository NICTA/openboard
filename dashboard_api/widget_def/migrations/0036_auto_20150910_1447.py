# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dashboard_api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0035_geodataset_ext_extra'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoColourPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=4)),
                ('colour', models.CharField(max_length=6, validators=[dashboard_api.validators.validate_html_colour])),
            ],
            options={
                'ordering': ('scale', 'value'),
            },
        ),
        migrations.CreateModel(
            name='GeoColourScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.SlugField(unique=True)),
                ('autoscale', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='geocolourpoint',
            name='scale',
            field=models.ForeignKey(to='widget_def.GeoColourScale'),
        ),
        migrations.AlterUniqueTogether(
            name='geocolourpoint',
            unique_together=set([('scale', 'value')]),
        ),
    ]
