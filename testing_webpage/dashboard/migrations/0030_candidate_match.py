# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-21 02:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0029_auto_20180221_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='match',
            field=models.FloatField(default=None, null=True),
        ),
    ]
