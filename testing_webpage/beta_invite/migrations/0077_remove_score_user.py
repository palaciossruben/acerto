# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-10 15:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0076_campaign_removed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='user',
        ),
    ]
