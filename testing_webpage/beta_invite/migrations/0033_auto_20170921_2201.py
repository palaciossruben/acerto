# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-21 22:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0032_auto_20170921_2126'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='cut_score_percentage',
            new_name='cut_score',
        ),
    ]
