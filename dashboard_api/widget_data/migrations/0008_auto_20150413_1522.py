# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0007_widgetdata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='widgetdata',
            old_name='real_frequency_text',
            new_name='actual_frequency_text',
        ),
    ]
