# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-26 23:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_state_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='salary',
            field=models.CharField(default='', max_length=100),
        ),
    ]
