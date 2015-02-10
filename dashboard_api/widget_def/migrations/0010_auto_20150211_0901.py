# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0009_auto_20150210_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('sort_order', models.IntegerField()),
                ('category', models.ForeignKey(to='widget_def.Category')),
            ],
            options={
                'ordering': ('category', 'sort_order'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='subcategory',
            unique_together=set([('category', 'sort_order'), ('category', 'name')]),
        ),
    ]
