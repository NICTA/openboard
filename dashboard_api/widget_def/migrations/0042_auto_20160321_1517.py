# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0041_auto_20160318_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewWidgetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField()),
                ('child_view_text', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('view', 'sort_order'),
            },
        ),
        migrations.AlterField(
            model_name='viewtype',
            name='show_children',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='widgetview',
            name='requires_authentication',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='viewwidgetdeclaration',
            name='child_view',
            field=models.ForeignKey(related_name='declarations', blank=True, to='widget_def.WidgetView', null=True),
        ),
        migrations.AddField(
            model_name='viewwidgetdeclaration',
            name='definition',
            field=models.ForeignKey(to='widget_def.WidgetDefinition'),
        ),
        migrations.AddField(
            model_name='viewwidgetdeclaration',
            name='view',
            field=models.ForeignKey(related_name='widgets', to='widget_def.WidgetView'),
        ),
        migrations.AlterUniqueTogether(
            name='viewwidgetdeclaration',
            unique_together=set([('view', 'sort_order'), ('definition', 'view')]),
        ),
    ]
