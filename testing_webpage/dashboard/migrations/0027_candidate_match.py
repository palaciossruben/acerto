# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-12 01:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_remove_candidate_scores'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='match',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
