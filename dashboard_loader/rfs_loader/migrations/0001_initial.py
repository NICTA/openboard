# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region', models.CharField(unique=True, max_length=50)),
                ('rating', models.IntegerField()),
                ('last_featured', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
