# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-06 18:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_candidate_scores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='scores',
        ),
    ]
