# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-13 19:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0031_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessuser',
            name='added',
            field=models.BooleanField(default=False),
        ),
    ]
