# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-15 01:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0137_auto_20180911_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='curriculum_s3_url',
            field=models.CharField(default='#', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='curriculum_url',
            field=models.CharField(default='#', max_length=200, null=True),
        ),
    ]
