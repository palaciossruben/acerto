# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-07 00:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0072_remove_survey_test_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='user',
        ),
    ]