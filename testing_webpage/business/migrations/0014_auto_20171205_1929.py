# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-05 19:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0013_auto_20171205_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plan',
            old_name='time_in_days',
            new_name='time',
        ),
    ]
