# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-19 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0160_user_scores'),
    ]

    operations = [
        migrations.AddField(
            model_name='testtype',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
