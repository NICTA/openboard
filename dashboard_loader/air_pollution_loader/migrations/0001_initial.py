# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0038_auto_20150325_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollutionRotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region', models.CharField(max_length=80)),
                ('last_featured', models.DateTimeField()),
                ('location', models.ForeignKey(to='widget_def.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='pollutionrotation',
            unique_together=set([('location', 'region')]),
        ),
    ]
