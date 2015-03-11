# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beach_quality_loader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beachsummaryhistory',
            name='region',
            field=models.CharField(max_length=5, choices=[(b'SYDHB', b'Sydney Harbour'), (b'PIWAT', b'Pittwater'), (b'SYDOC', b'Sydney Ocean'), (b'CTRCT', b'Central Coast'), (b'HUNTR', b'Hunter'), (b'ILLAW', b'Illawarra'), (b'BOTNY', b'Botany Bay, Georges River and Port Hacking')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='currentbeachrating',
            name='region',
            field=models.CharField(max_length=5, choices=[(b'SYDHB', b'Sydney Harbour'), (b'PIWAT', b'Pittwater'), (b'SYDOC', b'Sydney Ocean'), (b'CTRCT', b'Central Coast'), (b'HUNTR', b'Hunter'), (b'ILLAW', b'Illawarra'), (b'BOTNY', b'Botany Bay, Georges River and Port Hacking')]),
            preserve_default=True,
        ),
    ]
