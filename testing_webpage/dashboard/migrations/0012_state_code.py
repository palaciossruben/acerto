# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-22 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_candidate_removed'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='code',
            field=models.CharField(default='BL', max_length=10),
        ),
    ]
