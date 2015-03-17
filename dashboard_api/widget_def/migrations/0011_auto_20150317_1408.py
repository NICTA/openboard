# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def split_themes(apps, schemes_editor):
    WidgetDeclaration = apps.get_model("widget_def", "WidgetDeclaration")
    for wd in WidgetDeclaration.objects.all():
        if wd.theme is None:
            for theme in wd.themes.all():
                new_wd = WidgetDeclaration(definition=wd.definition,
                                            theme=theme,
                                            frequency=wd.frequency,
                                            location=wd.location)
                new_wd.save()
            wd.delete() 

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0010_auto_20150317_1406'),
    ]

    operations = [
        migrations.RunPython(split_themes)
    ]
