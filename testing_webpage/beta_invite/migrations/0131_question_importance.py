# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-08-04 02:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0130_merge_20180801_0237'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='importance',
            field=models.FloatField(default=None, null=True),
        ),
    ]
