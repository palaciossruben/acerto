# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-11 01:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0135_question_internal_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
