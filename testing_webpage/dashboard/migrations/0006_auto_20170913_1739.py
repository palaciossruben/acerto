# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-13 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20170913_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='comment',
            field=models.CharField(default='', max_length=1000, null=True),
        ),
    ]