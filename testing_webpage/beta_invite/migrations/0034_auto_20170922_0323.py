# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-22 03:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0033_auto_20170921_2201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questiontype',
            name='name_es',
        ),
        migrations.AddField(
            model_name='questiontype',
            name='code',
            field=models.CharField(max_length=10, null=True),
        ),
    ]