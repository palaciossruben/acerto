# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-06 23:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0012_auto_20170629_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_mobile',
            field=models.NullBooleanField(),
        ),
    ]
