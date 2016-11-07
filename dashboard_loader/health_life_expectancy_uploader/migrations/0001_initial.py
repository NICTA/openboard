# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-07 00:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HealthLifeExpectancyData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.SmallIntegerField(choices=[(1, 'NSW'), (2, 'Vic'), (3, 'Qld'), (4, 'WA'), (5, 'SA'), (6, 'Tas'), (7, 'ACT'), (8, 'NT'), (100, 'Australia')])),
                ('year', models.SmallIntegerField()),
                ('financial_year', models.BooleanField()),
                ('multi_year', models.IntegerField(default=1)),
                ('males', models.DecimalField(decimal_places=1, max_digits=4)),
                ('females', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='healthlifeexpectancydata',
            unique_together=set([('state', 'year')]),
        ),
    ]
