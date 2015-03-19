# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0022_auto_20150319_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='WidgetFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('url', models.SlugField(unique=True)),
                ('source_url', models.URLField(max_length=400)),
                ('subcategory', models.ForeignKey(to='widget_def.Subcategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='widgetdefinition',
            name='family',
            field=models.ForeignKey(blank=True, to='widget_def.WidgetFamily', null=True),
            preserve_default=True,
        ),
    ]
