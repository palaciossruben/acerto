# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-09 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0066_country_calling_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='added',
            field=models.BooleanField(default=False),
        ),
    ]
