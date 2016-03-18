# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0039_auto_20150923_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=120)),
                ('property_type', models.SmallIntegerField(choices=[(0, b'integer'), (1, b'string'), (2, b'boolean'), (3, b'decimal')])),
                ('strval', models.CharField(max_length=255, null=True, blank=True)),
                ('intval', models.IntegerField(null=True, blank=True)),
                ('boolval', models.NullBooleanField()),
                ('decval', models.DecimalField(null=True, max_digits=14, decimal_places=4, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ViewType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=120)),
                ('show_children', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='WidgetView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120)),
                ('label', models.SlugField(unique=True)),
                ('sort_order', models.IntegerField()),
                ('requires_authentication', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, to='widget_def.WidgetView', null=True)),
            ],
            options={
                'ordering': ('parent', 'sort_order'),
            },
        ),
        migrations.AlterModelOptions(
            name='trafficlightautorule',
            options={'ordering': ('strategy', 'default_val', '-min_val', 'map_val')},
        ),
        migrations.AddField(
            model_name='viewproperty',
            name='view',
            field=models.ForeignKey(to='widget_def.WidgetView'),
        ),
        migrations.AlterUniqueTogether(
            name='widgetview',
            unique_together=set([('parent', 'sort_order'), ('parent', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='viewproperty',
            unique_together=set([('view', 'key')]),
        ),
    ]
