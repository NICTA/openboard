# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=5)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoadSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=5)),
                ('origin', models.CharField(max_length=80)),
                ('destination', models.CharField(max_length=80)),
                ('direction', models.CharField(max_length=20)),
                ('length', models.IntegerField(null=True, blank=True)),
                ('road', models.ForeignKey(to='travel_speed_loader.Road')),
            ],
            options={
                'ordering': ('road', 'label'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='roadsection',
            unique_together=set([('road', 'origin', 'destination'), ('road', 'label')]),
        ),
    ]
