# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-13 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0179_remove_campaign_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='added',
            field=models.BooleanField(default=False),
        ),
    ]