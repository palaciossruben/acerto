# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-05 16:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0120_auto_20180626_0510'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='excluding',
            field=models.BooleanField(default=False),
        ),
    ]