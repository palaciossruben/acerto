# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-23 22:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0015_campaign_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='campaign_id',
            new_name='campaign',
        ),
    ]
