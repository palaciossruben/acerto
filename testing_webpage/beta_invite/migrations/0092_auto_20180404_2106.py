# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-05 02:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0091_user_gender'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='gender',
            table='genders',
        ),
    ]