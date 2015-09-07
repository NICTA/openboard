# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0011_auto_20150904_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geofeature',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, blank=True),
        ),
    ]
