# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-15 04:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0015_auto_20171215_0441'),
    ]

    operations = [
        migrations.RenameModel('User', 'BusinessUser')
    ]