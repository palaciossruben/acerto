# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-07 01:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0102_auto_20180427_0436'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['pk']},
        ),
    ]
