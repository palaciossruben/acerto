# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-30 03:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0049_stateevent_use_machine_learning'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='filename',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
