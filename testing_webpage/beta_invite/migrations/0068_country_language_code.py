# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-17 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0067_user_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='language_code',
            field=models.CharField(default='es', max_length=3),
        ),
    ]
