# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-21 02:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_auto_20180213_0330'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='match',
            new_name='text_match',
        ),
    ]