# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-24 20:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0040_candidate_evaluation_summary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessstate',
            name='candidates',
        ),
        migrations.RemoveField(
            model_name='businessstate',
            name='evaluation',
        ),
    ]