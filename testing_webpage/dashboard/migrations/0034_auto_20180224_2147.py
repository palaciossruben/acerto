# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-24 21:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_candidate_explanation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='explanation',
            new_name='screening_explanation',
        ),
    ]