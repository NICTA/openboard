# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agency_id', models.CharField(unique=True, max_length=10)),
                ('agency_name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service_id', models.CharField(unique=True, max_length=20)),
                ('monday', models.BooleanField(default=True)),
                ('tuesday', models.BooleanField(default=True)),
                ('wednesday', models.BooleanField(default=True)),
                ('thursday', models.BooleanField(default=True)),
                ('friday', models.BooleanField(default=True)),
                ('saturday', models.BooleanField(default=True)),
                ('sunday', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exception_date', models.DateField()),
                ('exception_type', models.SmallIntegerField(choices=[(1, b'Added'), (2, b'Removed')])),
                ('calendar', models.ForeignKey(to='transport_static_loader.Calendar')),
            ],
            options={
                'ordering': ('calendar', 'exception_date'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('route_id', models.CharField(unique=True, max_length=20)),
                ('short_name', models.CharField(max_length=50, null=True, blank=True)),
                ('long_name', models.CharField(max_length=500)),
                ('network', models.CharField(max_length=200)),
                ('service_type', models.SmallIntegerField(choices=[(0, b'Light Rail Service'), (1, b'Subway Service'), (2, b'Train Service'), (3, b'Bus Service'), (4, b'Ferry Service')])),
                ('colour', models.CharField(max_length=6)),
                ('text_colour', models.CharField(max_length=6)),
                ('agency', models.ForeignKey(to='transport_static_loader.Agency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stop_id', models.CharField(unique=True, max_length=20)),
                ('transit_stop_number', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(max_digits=16, decimal_places=13)),
                ('longitude', models.DecimalField(max_digits=16, decimal_places=13)),
                ('is_parent_station', models.BooleanField(default=False)),
                ('wheelchair_boarding', models.NullBooleanField()),
                ('platform_number', models.CharField(max_length=50, null=True, blank=True)),
                ('parent_station', models.ForeignKey(blank=True, to='transport_static_loader.Stop', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StopTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stop_sequence', models.SmallIntegerField()),
                ('arrival_time_day_offset', models.SmallIntegerField(default=0)),
                ('arrival_time', models.TimeField(null=True, blank=True)),
                ('departure_time_day_offset', models.SmallIntegerField(default=0)),
                ('departure_time', models.TimeField(null=True, blank=True)),
                ('headsign', models.CharField(max_length=200, null=True, blank=True)),
                ('pickup_type', models.SmallIntegerField(choices=[(0, b'Regularly scheduled pickup/dropoff'), (1, b'No pickup/dropoff available'), (2, b'Must phone agency to arrange pickup/dropoff'), (3, b'Must coordinate with driver to arrange pickup/dropoff')])),
                ('dropoff_type', models.SmallIntegerField(choices=[(0, b'Regularly scheduled pickup/dropoff'), (1, b'No pickup/dropoff available'), (2, b'Must phone agency to arrange pickup/dropoff'), (3, b'Must coordinate with driver to arrange pickup/dropoff')])),
                ('shape_dist_travelled', models.DecimalField(max_digits=16, decimal_places=10)),
                ('stop', models.ForeignKey(to='transport_static_loader.Stop')),
            ],
            options={
                'ordering': ('trip', 'stop_sequence'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_id', models.CharField(unique=True, max_length=50)),
                ('shape_id', models.CharField(max_length=50)),
                ('headsign', models.CharField(max_length=200)),
                ('main_direction', models.BooleanField(default=False)),
                ('block_id', models.CharField(max_length=20, null=True, blank=True)),
                ('wheelchair_accessible', models.NullBooleanField()),
                ('calendar', models.ForeignKey(to='transport_static_loader.Calendar')),
                ('route', models.ForeignKey(to='transport_static_loader.Route')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stoptime',
            name='trip',
            field=models.ForeignKey(to='transport_static_loader.Trip'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='stoptime',
            unique_together=set([('trip', 'stop_sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='calendardate',
            unique_together=set([('calendar', 'exception_date')]),
        ),
    ]
