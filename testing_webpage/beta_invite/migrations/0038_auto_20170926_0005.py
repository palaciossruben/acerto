# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-26 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0037_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='passed',
            field=models.BooleanField(),
        ),
    ]
