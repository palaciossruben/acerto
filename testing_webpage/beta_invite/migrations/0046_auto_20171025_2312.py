# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-25 23:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0045_auto_20171024_1704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='additional_params',
            new_name='params',
        ),
    ]