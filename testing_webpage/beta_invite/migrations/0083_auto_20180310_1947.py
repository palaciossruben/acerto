# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-10 19:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0082_campaign_with_email_in_form'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='with_email_in_form',
            new_name='has_email_in_form',
        ),
    ]
