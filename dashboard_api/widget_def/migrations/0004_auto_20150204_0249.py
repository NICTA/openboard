# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0003_auto_20150203_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='WidgetDeclaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('definition', models.ForeignKey(to='widget_def.WidgetDefinition')),
                ('frequency', models.ForeignKey(to='widget_def.Frequency')),
                ('location', models.ForeignKey(to='widget_def.Location')),
                ('themes', models.ManyToManyField(to='widget_def.Theme')),
            ],
            options={
                'ordering': ('location', 'frequency', 'definition'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='widgetdeclaration',
            unique_together=set([('location', 'frequency', 'definition')]),
        ),
        migrations.AlterModelOptions(
            name='tiledefinition',
            options={'ordering': ['widget', 'expansion', 'sort_order']},
        ),
        migrations.AlterModelOptions(
            name='widgetdefinition',
            options={'ordering': ('category', 'sort_order')},
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='am_pm',
            field=models.BooleanField(default=False, help_text=b'Only used for single_main_stat type tiles'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='expansion',
            field=models.BooleanField(default=False, help_text=b'A widget must have one and only one non-expansion tile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiledefinition',
            name='sort_order',
            field=models.IntegerField(help_text=b'Note: The default (non-expansion) tile is always sorted first'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trafficlightscalecode',
            name='sort_order',
            field=models.IntegerField(help_text=b'"Good" codes should have lower sort order than "Bad" codes.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='widgetdefinition',
            name='refresh_rate',
            field=models.IntegerField(help_text=b'in seconds'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('name', 'actual_frequency'), ('category', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='themes',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='location',
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='frequency',
        ),
    ]
