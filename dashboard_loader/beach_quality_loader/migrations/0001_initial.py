# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BeachSummaryHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(auto_now=True)),
                ('region', models.CharField(max_length=5, choices=[(b'SYDHB', b'Sydney Harbour'), (b'PIWAT', b'Pittwater'), (b'SYDOC', b'Sydney Ocean'), (b'CTRCT', b'Central Coast'), (b'ILLAW', b'Illawarra'), (b'BOTNY', b'Botany Bay, Georges River and Port Hacking')])),
                ('num_pollution_unlikely', models.IntegerField()),
                ('num_pollution_possible', models.IntegerField()),
                ('num_pollution_likely', models.IntegerField()),
            ],
            options={
                'ordering': ('day', 'region'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CurrentBeachRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region', models.CharField(max_length=5, choices=[(b'SYDHB', b'Sydney Harbour'), (b'PIWAT', b'Pittwater'), (b'SYDOC', b'Sydney Ocean'), (b'CTRCT', b'Central Coast'), (b'ILLAW', b'Illawarra'), (b'BOTNY', b'Botany Bay, Georges River and Port Hacking')])),
                ('beach_name', models.CharField(max_length=100)),
                ('rating', models.SmallIntegerField(choices=[(1, b'Pollution is unlikely. Enjoy your swim!'), (2, b'Pollution is possible. Take care.'), (3, b'Pollution is likely. Avoid swimming today.')])),
                ('day_updated', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ('region', 'beach_name', '-rating'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='currentbeachrating',
            unique_together=set([('region', 'beach_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='beachsummaryhistory',
            unique_together=set([('day', 'region')]),
        ),
    ]
