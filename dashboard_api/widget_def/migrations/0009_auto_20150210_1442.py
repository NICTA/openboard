# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0008_auto_20150205_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='IconCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.SlugField()),
                ('description', models.CharField(max_length=80)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ['scale', 'sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IconLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='iconcode',
            name='scale',
            field=models.ForeignKey(to='widget_def.IconLibrary'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='iconcode',
            unique_together=set([('scale', 'sort_order'), ('scale', 'value')]),
        ),
        migrations.AddField(
            model_name='statistic',
            name='icon_library',
            field=models.ForeignKey(blank=True, to='widget_def.IconLibrary', null=True),
            preserve_default=True,
        ),
    ]
