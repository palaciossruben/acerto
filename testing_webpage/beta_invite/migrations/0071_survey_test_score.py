# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-01 19:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0070_auto_20180124_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='test_score',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Score'),
        ),
    ]