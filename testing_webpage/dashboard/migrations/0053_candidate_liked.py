# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-11 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0052_candidate_change_by_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='liked',
            field=models.BooleanField(default=False),
        ),
    ]