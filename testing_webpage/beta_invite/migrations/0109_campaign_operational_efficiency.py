# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-11 03:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0108_auto_20180610_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='operational_efficiency',
            field=models.FloatField(null=True),
        ),
    ]
