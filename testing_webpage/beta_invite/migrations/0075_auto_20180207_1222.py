# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-07 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0074_evaluation_scores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluation',
            name='scores',
        ),
        migrations.AddField(
            model_name='score',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.User'),
        ),
    ]
