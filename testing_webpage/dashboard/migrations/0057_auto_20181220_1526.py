# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-20 20:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0056_merge_20181217_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='change_by_client',
            new_name='change_by_person',
        ),
    ]