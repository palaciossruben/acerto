# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-06 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0055_user_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='calendly',
            field=models.BooleanField(default=True),
        ),
    ]