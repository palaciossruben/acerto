# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-09 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0182_auto_20181214_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtype',
            name='send_more_than_ones',
            field=models.BooleanField(default=False),
        ),
    ]
